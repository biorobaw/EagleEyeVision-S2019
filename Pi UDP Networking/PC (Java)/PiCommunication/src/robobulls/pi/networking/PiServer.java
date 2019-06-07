package robobulls.pi.networking;

import com.sun.istack.internal.Nullable;

import java.net.*;
import java.io.*;
import java.util.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

/**
 * Sends and receives UDP packets from connected PiBots.
 */
public class PiServer
{
    static final int MAX_BUFFER_SIZE = 65535; // In bytes
    static final int DEBUG = 2; // 0 to 2; higher number = more debug messages

    long startTime;
    final ByteOrder serverEndian;
    final PiBotBase[] pibots;
    final int maxPiBots;
    final ArrayList<PiMessageInfo> sentMessages = new ArrayList<>();

    private DatagramSocket serverSocket;
    private final int serverPort;
    private int nextPacketNum = 1000; // Arbitrary starting number
    private final PiConnectionListener connectionListenerThread;
    private final PiConnectionHelper connectionHelperThread;

    /**
     * Constructs the Pi server.
     *
     * @param port   Port to use for the server
     * @param endian Endianness to use for PiBot communication
     */
    public PiServer(int port, ByteOrder endian, int maxPiBots)
    {
        this.serverPort = port;
        this.serverEndian = endian;
        this.maxPiBots = maxPiBots;

        pibots = new PiBotBase[maxPiBots];

        connectionHelperThread = new PiConnectionHelper(this);
        connectionListenerThread = new PiConnectionListener(this);
    }

    /**
     * Sets up the server and listens for packets on a new thread.
     * Call this method before doing anything else.
     */
    public void start()
    {
        if (serverSocket != null)
        {
            throw new RuntimeException("PiServer already started");
        }

        try
        {
            serverSocket = new DatagramSocket(serverPort);
            serverSocket.setSoTimeout(0);
        }
        catch (SocketException e)
        {
            throw new RuntimeException(e);
        }

        startTime = System.currentTimeMillis();

        connectionListenerThread.start();
        connectionHelperThread.start();
    }

    /**
     * Stops listening for packets and closes the server.
     * Call this method when you intend to never use the server again.
     */
    public void stop()
    {
        if (serverSocket == null)
        {
            throw new RuntimeException("PiServer not running");
        }

        for (int i = 0; i < maxPiBots; i++)
        {
            PiBotBase pibot = pibots[i];
            if (pibot == null || pibot.status == PiConnectionStatus.OFFLINE)
                continue;

            sendMessage(pibot, PiNetworkCommand.SHUTDOWN, null);
        }

        serverSocket.close();

        connectionListenerThread.stopRunning();

        try
        {
            connectionListenerThread.join();
        }
        catch (InterruptedException e)
        {
            // Do nothing
        }

        connectionHelperThread.stopRunning();

        try
        {
            connectionHelperThread.join();
        }
        catch (InterruptedException e)
        {
            // Do nothing
        }

        serverSocket = null;
    }
    
    /**
     * Begins tracking the PiBot for any received messages and status changes
     *
     * @param pibot The PiBot to track
     */
    public void trackPiBot(PiBotBase pibot)
    {
        if (pibot.id >= maxPiBots)
        {
            throw new RuntimeException("PiBot ID is invalid");
        }

        PiBotBase oldPiBot = pibots[pibot.id];
        
        // Check if a PiBot is already being tracked (this might have happened automatically)
        if (oldPiBot != null)
        {
            // Check if old PiBot is not a PiBotBase (the old pibot might contain custom data that could be lost)
            if (oldPiBot.getClass() != PiBotBase.class)
            {
                throw new RuntimeException("PiBot with ID " + pibot.id + " is already being tracked");
            }
            else
            {
                // Safe to replace old PiBot

                if (pibot.ip == null || pibot.port == 0)
                {
                    // Replace new PiBot's IP/port with known working values
                    pibot.ip = oldPiBot.ip;
                    pibot.port = oldPiBot.port;
                }

                // Replace new PiBot's remaining info with known working values
                pibot.heartbeatReceiveTime = oldPiBot.heartbeatReceiveTime;
                pibot.status = oldPiBot.status;
            }
        }

        pibots[pibot.id] = pibot;
    }

    /**
     * Stops tracking the PiBot for any received messages and status changes
     *
     * @param pibot The PiBot to stop tracking
     */
    public void untrackPiBot(PiBotBase pibot)
    {
        if (pibots[pibot.id] != pibot)
        {
            throw new RuntimeException("PiBot is not being tracked");
        }

        pibots[pibot.id] = null;
    }

    /**
     * Sends a message to the specified PiBot.
     * @param pibot The PiBot
     * @param data The user data to send
     */
    public void sendMessage(PiBotBase pibot, byte[] data)
    {
        sendMessage(pibot, PiNetworkCommand.USER_MESSAGE, data);
    }

    /**
     * Sends a message to the specified PiBot.
     *
     * @param pibot   The PiBot to send the message to
     * @param command The command within the message
     * @param data    The additional data within the message, if any
     */
    void sendMessage(PiBotBase pibot, PiNetworkCommand command, @Nullable byte[] data)
    {
        synchronized (this)
        {
            int packetNum = nextPacketNum++;

            byte[] sendBuffer;
            ByteBuffer byteBuffer;

            if (data != null)
            {
                sendBuffer = new byte[8 + data.length];

                byteBuffer = ByteBuffer.wrap(sendBuffer);
                byteBuffer.putInt(packetNum);
                byteBuffer.putInt(command.getInt());
                byteBuffer.put(data);
            }
            else
            {
                sendBuffer = new byte[8];

                byteBuffer = ByteBuffer.wrap(sendBuffer);
                byteBuffer.putInt(packetNum);
                byteBuffer.putInt(command.getInt());
            }

            DatagramPacket sendPacket = new DatagramPacket(sendBuffer, sendBuffer.length, pibot.ip, pibot.port);
            long currentTime = System.currentTimeMillis();

            if (command == PiNetworkCommand.USER_MESSAGE)
            {
                if (pibot.status == PiConnectionStatus.TIMEOUT)
                {
                    System.err.println("Attempting to send message to timed out pibot " + pibot.id + "!");
                }
                else if (pibot.status == PiConnectionStatus.OFFLINE)
                {
                    System.err.println("Attempting to send message to disconnected pibot " + pibot.id + "!");
                }

                PiMessageInfo messageInfo = new PiMessageInfo(sendPacket, currentTime, packetNum);
                sentMessages.add(messageInfo);
            }

            if (DEBUG >= 2)
            {
                float elapsedTime = (currentTime - startTime) / 1000.0f;
                System.out.printf("<- %-15s\tMy ID:\t%6d\tTime:\t%8.3f\n", command, packetNum, elapsedTime);
            }

            try
            {
                sendDatagramPacket(sendPacket);
            }
            catch (IOException e)
            {
                e.printStackTrace();
            }
        }
    }

    /**
     * Send a datagram packet using the server's socket
     * @param packet The packet to send
     * @throws IOException Send exception
     */
    void sendDatagramPacket(DatagramPacket packet) throws IOException
    {
        serverSocket.send(packet);
    }

    /**
     * Waits until a packet is received using the server's socket
     * @param receiveBuffer The receive buffer to use
     * @return The received packet
     * @throws IOException Receive exception
     */
    DatagramPacket receiveDatagramPacket(byte[] receiveBuffer) throws IOException
    {
        DatagramPacket packet = new DatagramPacket(receiveBuffer, receiveBuffer.length);

        serverSocket.receive(packet);

        return packet;
    }
}

