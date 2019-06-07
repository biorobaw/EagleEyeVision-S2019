package robobulls.pi.networking;

import java.net.InetAddress;
import java.util.ArrayList;

/**
 * Stores information about a PiBot.
 */
public class PiBotBase
{
    int id;
    InetAddress ip;
    int port;
    long heartbeatReceiveTime;
    PiConnectionStatus status = PiConnectionStatus.OFFLINE;

    private final ArrayList<PiMessageListener> listeners = new ArrayList<>();

    public PiBotBase(int id)
    {
        if (id < 0)
        {
            throw new RuntimeException("Invalid PiBot ID");
        }

        this.id = id;
    }

    public int getID()
    {
        return id;
    }

    public InetAddress getIP()
    {
        return ip;
    }

    public int getPort()
    {
        return port;
    }

    public PiConnectionStatus getStatus()
    {
        return status;
    }

    /**
     * Waits until the PiBot's status is online.
     */
    public void waitUntilOnline()
    {
        while (status != PiConnectionStatus.ONLINE)
        {
            try
            {
                Thread.sleep(10);
            }
            catch (InterruptedException e)
            {
                e.printStackTrace();
            }
        }
    }

    /**
     * Registers a listener for when the server receives PiBot messages.
     *
     * @param listener The class containing the callback function
     */
    synchronized public void addPiMessageListener(PiMessageListener listener)
    {
        if (listeners.contains(listener))
        {
            throw new RuntimeException("Listener already added");
        }

        listeners.add(listener);
    }

    /**
     * Unregisters a previously registered listener.
     *
     * @param listener The class containing the callback function
     */
    synchronized public void removePiMessageListener(PiMessageListener listener)
    {
        if (!listeners.remove(listener))
        {
            throw new RuntimeException("Listener did not exist");
        }
    }

    /**
     * Stores the status of the PiBot and raises the status changed event
     * @param status The new status
     */
    synchronized void setStatus(PiConnectionStatus status)
    {
        this.status = status;

        for (PiMessageListener listener : listeners)
        {
            listener.onStatusChanged(this);
        }
    }

    /**
     * Raises the message received event for the PiBot.
     * @param data The data that it received
     */
    synchronized void raiseMessageReceived(byte[] data)
    {
        for (PiMessageListener listener : listeners)
        {
            listener.onMessageReceived(this, data);
        }
    }
}
