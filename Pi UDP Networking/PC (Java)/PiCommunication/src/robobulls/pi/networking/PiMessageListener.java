package robobulls.pi.networking;

/**
 * Notifies when a PiBot sends a message.
 */
public interface PiMessageListener
{
    /**
     * Method to be called when the PiBot sends a message.
     * @param piBotBase The PiBot that sent the message
     * @param data The data within the message
     */
    void onMessageReceived(PiBotBase piBotBase, byte[] data);

    /**
     * Method to be called when the PiBot changes status.
     * @param piBotBase The PiBot that changed
     */
    void onStatusChanged(PiBotBase piBotBase);
}