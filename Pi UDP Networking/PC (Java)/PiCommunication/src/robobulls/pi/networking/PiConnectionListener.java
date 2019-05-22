package robobulls.pi.networking;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.util.Arrays;

/**
 * Listens for packets from PiBots.
 */
class PiConnectionListener extends Thread
{
    private final PiServer server;

    private volatile boolean running = false;

    PiConnectionListener(PiServer server)
    {
        this.server = server;
    }

    /**
     * Listens for UDP packets.
     * Don't call this method directly.
     */
    public void run()
    {
        byte[] receiveBuffer = new byte[PiServer.MAX_BUFFER_SIZE];
        DatagramPacket receivePacket;

        running = true;

        while (running)
        {
            try
            {
                receivePacket = server.receiveDatagramPacket(receiveBuffer);
            }
            catch (IOException e)
            {
                // An exception may occur due to close() being called, so ignore any exceptions
                //e.printStackTrace();
                continue;
            }

            processPacket(receivePacket);
        }

        if (PiServer.DEBUG >= 1)
        {
            System.out.println("Exiting PiConnectionListener");
        }
    }

    void stopRunning()
    {
        running = false;

        this.interrupt();
    }

    /**
     * Processes a PiBot packet and notifies any listeners.
     *
     * @param packet The received PiBot packet
     */
    private void processPacket(DatagramPacket packet)
    {
        synchronized (server)
        {
            InetAddress ip = packet.getAddress();
            int port = packet.getPort();
            byte[] packetData = packet.getData();

            ByteBuffer byteBuffer = ByteBuffer.wrap(packetData).order(server.serverEndian);
            int packetNum = byteBuffer.getInt();
            int id = byteBuffer.getInt();
            int commandID = byteBuffer.getInt();
            PiNetworkCommand command = PiNetworkCommand.getEnum(commandID);
            byte[] msgData = null;
            PiBotBase pibot = server.pibots[id];
            long currentTime = System.currentTimeMillis();

            if (packet.getLength() > 12)
            {
                msgData = Arrays.copyOfRange(packetData, 12, packet.getLength());
            }

            if (pibot == null)
            {
                System.err.println("Message received from unknown PiBot with ID " + id);

                return;
                // Create pibot if it doesn't exist
                /*if (PiServer.DEBUG >= 1)
                {
                    System.out.println("PiBot " + id + " was added.");
                }

                pibot = new PiBotBase(id);
                server.pibots[id] = pibot;*/
            }

            // Check if pibot has no ip/port set yet
            if (pibot.ip == null || pibot.port == 0)
            {
                pibot.ip = ip;
                pibot.port = port;

                pibot.setStatus(PiConnectionStatus.ONLINE);
                pibot.heartbeatReceiveTime = System.currentTimeMillis();
            }
            else if (!pibot.ip.equals(ip) || pibot.port != port) // Check if ip/port changed
            {
                if (PiServer.DEBUG >= 1)
                {
                    System.err.println("PiBot " + id + "'s IP/port changed!");
                }

                pibot.ip = ip;
                pibot.port = port;
            }

            switch (command)
            {
                case HEARTBEAT:
                    if (PiServer.DEBUG >= 2)
                    {
                        float elapsedTime = (currentTime - server.startTime) / 1000.0f;
                        System.out.printf("-> %-15s\tPi ID:\t%6d\tTime:\t%8.3f\n", command, packetNum, elapsedTime);
                    }

                    pibot.heartbeatReceiveTime = System.currentTimeMillis();
                    break;
                case SHUTDOWN:
                    if (PiServer.DEBUG >= 2)
                    {
                        float elapsedTime = (currentTime - server.startTime) / 1000.0f;
                        System.out.printf("-> %-15s\tPi ID:\t%6d\tTime:\t%8.3f\n", command, packetNum, elapsedTime);
                    }

                    System.out.println("PiBot " + id + " is shutting down.");

                    pibot.setStatus(PiConnectionStatus.OFFLINE);
                    pibot.heartbeatReceiveTime = 0;

                    break;
                case ACK:
                    if (PiServer.DEBUG >= 2)
                    {
                        float elapsedTime = (currentTime - server.startTime) / 1000.0f;
                        System.out.printf("-> %-15s\tMy ID:\t%6d\tTime:\t%8.3f\n", command, packetNum, elapsedTime);
                    }

                    for (int i = 0; i < server.sentMessages.size(); i++)
                    {
                        PiMessageInfo info = server.sentMessages.get(i);

                        if (info.packetNum == packetNum)
                        {
                            server.sentMessages.remove(i);
                            break;
                        }
                    }

                    break;
                case USER_MESSAGE:
                    if (PiServer.DEBUG >= 2)
                    {
                        float elapsedTime = (currentTime - server.startTime) / 1000.0f;
                        System.out.printf("-> %-15s\tPi ID:\t%6d\tTime:\t%8.3f\n", command, packetNum, elapsedTime);
                    }

                    byte[] ackBuffer = new byte[8];

                    ByteBuffer ackByteBuffer = ByteBuffer.wrap(ackBuffer);
                    ackByteBuffer.putInt(packetNum);
                    ackByteBuffer.putInt(PiNetworkCommand.ACK.getInt());

                    DatagramPacket ackPacket = new DatagramPacket(ackBuffer, ackBuffer.length, pibot.ip, pibot.port);

                    try
                    {
                        server.sendDatagramPacket(ackPacket);
                    }
                    catch (IOException e)
                    {
                        e.printStackTrace();
                    }

                    pibot.raiseMessageReceived(msgData);

                    break;
                default:
                    System.err.println("Unexpected PiNetworkCommand");

                    break;
            }
        }
    }
}