package robobulls.pi.networking;

import java.io.IOException;

/**
 * Checks for heartbeats from a PiBot, sends heartbeats to PiBots, and checks for timed out packets.
 */
class PiConnectionHelper extends Thread
{
    // Heartbeat settings
    private static final int HEARTBEAT_SEND_RATE = 4000; // How often to SEND a heartbeat, in ms.
    private static final int HEARTBEAT_TIMEOUT = 4500; // Maximum allowed time between RECEIVED heartbeats, in ms.
    private static final int ACK_CHECK_RATE = 10; // How often to check for timed out packets, in ms
    private static final int ACK_TIMEOUT = 50; // Maximum allowed time for a RECEIVED packet acknowledgement, in ms

    private final PiServer server;

    private volatile boolean running = false;

    PiConnectionHelper(PiServer server)
    {
        this.server = server;
    }

    public void run()
    {
        long heartbeatCheckTime = System.currentTimeMillis();
        long heartbeatSendTime = System.currentTimeMillis();
        long ackTime = System.currentTimeMillis();

        running = true;

        while (running)
        {
            try
            {
                // Sleep an arbitrary amount of time
                sleep(10);
            }
            catch (InterruptedException e)
            {
                // Occurs when PiServer calls interrupt()
                break;
            }

            long currentTime = System.currentTimeMillis();

            if (currentTime >= heartbeatCheckTime + HEARTBEAT_SEND_RATE)
            {
                checkHeartbeats();
                heartbeatCheckTime = currentTime;
            }

            if (currentTime >= heartbeatSendTime + HEARTBEAT_SEND_RATE)
            {
                sendHeartbeats();
                heartbeatSendTime = currentTime;
            }

            if (currentTime >= ackTime + ACK_CHECK_RATE)
            {
                checkAcks();
                ackTime = currentTime;
            }
        }

        System.out.println("EXIT THREAD 1");
    }

    void stopRunning()
    {
        running = false;

        this.interrupt();
    }

    /**
     * Checks all pibots for any missed heartbeats, or restored heartbeats.
     */
    private void checkHeartbeats()
    {
        synchronized (server)
        {
            long currentTime = System.currentTimeMillis();

            for (int i = 0; i < server.maxPiBots; i++)
            {
                PiBotBase pibot = server.pibots[i];
                if (pibot == null || pibot.ip == null || pibot.port == 0)
                    continue;

                // Check if the previous heartbeat was missed
                switch (pibot.status)
                {
                    case OFFLINE:
                    case TIMEOUT:
                        if (pibot.heartbeatReceiveTime > currentTime - HEARTBEAT_TIMEOUT)
                        {
                            if (PiServer.DEBUG >= 1)
                            {
                                System.out.println("PiBot " + i + " restored.");
                            }

                            pibot.setStatus(PiConnectionStatus.ONLINE);
                        }
                        break;
                    case ONLINE:
                        if (pibot.heartbeatReceiveTime < currentTime - HEARTBEAT_TIMEOUT)
                        {
                            if (PiServer.DEBUG >= 1)
                            {
                                System.err.println("PiBot " + i + " timed out. No heartbeat received.");
                            }

                            pibot.setStatus(PiConnectionStatus.TIMEOUT);
                        }
                        break;
                }
            }
        }
    }

    /**
     * Sends heartbeats to all pibots
     */
    private void sendHeartbeats()
    {
        synchronized (server)
        {
            long currentTime = System.currentTimeMillis();

            for (int i = 0; i < server.maxPiBots; i++)
            {
                PiBotBase pibot = server.pibots[i];
                if (pibot == null || pibot.ip == null || pibot.port == 0)
                    continue;

                // Send a new heartbeat as long as the pibot isn't offline
                // The Pibot itself will always send heartbeats to the server whenever it can.
                // Since the pibot may change its ip/port after restarting, the server does not need to repeatedly
                // send heartbeats when the pibot is shutdown.
                if (pibot.status != PiConnectionStatus.OFFLINE)
                {
                    server.sendMessage(pibot, PiNetworkCommand.HEARTBEAT, null);
                }
            }
        }
    }

    /**
     * Checks for timed out packets and resends them once before giving up
     */
    private void checkAcks()
    {
        synchronized (server)
        {
            long currentTime = System.currentTimeMillis();

            for (int i = 0; i < server.sentMessages.size(); i++)
            {
                PiMessageInfo info = server.sentMessages.get(i);

                if (info.sendTime < currentTime - ACK_TIMEOUT)
                {
                    info.sendTime = currentTime;

                    //if (PiServer.DEBUG >= 1)
                    {
                        System.err.println("Packet " + info.packetNum + " timed out. Resending...");
                    }

                    try
                    {
                        server.sendDatagramPacket(info.packet);
                    }
                    catch (IOException e)
                    {
                        e.printStackTrace();
                    }

                    // Assume second try is successful so packet can be removed from list
                    // I is decreased due to this being inside a for loop
                    server.sentMessages.remove(i--);
                }
            }
        }
    }
}