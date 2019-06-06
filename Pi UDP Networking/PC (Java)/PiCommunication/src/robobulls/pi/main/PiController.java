package robobulls.pi.main;

import com.sun.istack.internal.Nullable;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import robobulls.pi.networking.PiServer;
import robobulls.pi.networking.*;


/**
 * Example class that shows usage of the PiServer in order to communicate with PiBots.
 */
public class PiController implements PiMessageListener
{
    private static final int SERVER_PORT = 5555;
    private static final ByteOrder SERVER_ENDIAN = ByteOrder.BIG_ENDIAN;
    private static final int MAX_PIBOTS = 10;

    private PiServer network;
    private PiBot myPiBot; // Can be replaced with an array for controlling multiple PiBots

    /**
     * Constructs a Pi controller.
     */
    public PiController()
    {
    }

    /**
     * Starts the server and connects to PiBots.
     * Call this method before doing anything else.
     */
    public void start()
    {
        if (network != null)
        {
            throw new RuntimeException("Server already exists");
        }

        myPiBot = new PiBot(3);

        network = new PiServer(SERVER_PORT, SERVER_ENDIAN, MAX_PIBOTS);
        network.start();
        network.trackPiBot(myPiBot);

        System.out.println("Wait for pibot");
        myPiBot.waitUntilOnline();
        System.out.println("Got pibot");

        myPiBot.addPiMessageListener(this);
    }

    /**
     * Stops the controller and closes any open connections.
     * Call this method when you intend to never use the controller again.
     */
    public void stop()
    {
        if (network == null)
        {
            throw new RuntimeException("Server not running");
        }

        myPiBot.removePiMessageListener(this);

        network.stop();
        network.untrackPiBot(myPiBot);
        network = null;
    }

    /**
     * Method intended to be called frequently at a fixed interval.
     * It can be used to update variables or call functions.
     * @param msg Optional message provided by the user.
     */
    public void update(@Nullable String msg)
    {
        // Add additional logic as necessary
        if (msg != null)
        {
            // Placeholder random logic, replace everything below with something more useful
            byte[] data = new byte[16];
            ByteBuffer byteBuffer = ByteBuffer.wrap(data).order(SERVER_ENDIAN);

            String [] StrMsgArray = msg.split(",");
		    char temp_ch = msg.charAt(0);
		    String temp_str = StrMsgArray[1];
		    if (temp_ch < 'a' || temp_ch > 'z'){
		        System.out.println("Character error, defaulting to n");
		        temp_ch = 'n';
            }
		    if (temp_str.length() > 7){
		        System.out.println("String error, defaulting to NA");
		        temp_str = "NA";
            }
            System.out.println(temp_ch);
            System.out.println(temp_str);

            int num1 = 72;
            float num2 = 3.14f;
            char ch = temp_ch;
            //char ch = 't';
            boolean bool = true;
            String str = temp_str;
            //String str = "hello";

            byte[] strBytes = str.getBytes();

            byteBuffer.putInt(num1);
            byteBuffer.putFloat(num2);
            byteBuffer.put((byte)ch);
            byteBuffer.put(bool ? (byte)1 : (byte)0); // boolean converted to a byte
            byteBuffer.put(strBytes);

            network.sendMessage(myPiBot, data);
        }
    }

    /**
     * Automatically called when the controller receives a message.
     * Don't call this method directly.
     * @param piBotBase The PiBot that sent the message
     * @param data The data within the message
     */
    public void onMessageReceived(PiBotBase piBotBase, byte[] data)
    {
        if (!(piBotBase instanceof PiBot))
        {
            return;
        }

        PiBot pibot = (PiBot)piBotBase;

        // Add additional logic as necessary
        System.out.println("Received message from pibot " + pibot.getID());

        // Placeholder random logic, replace everything below with something more useful
        ByteBuffer byteBuffer = ByteBuffer.wrap(data);
        int num1 = byteBuffer.getInt();
        float num2 = byteBuffer.getFloat();
        char ch = (char)byteBuffer.get();
        boolean bool = byteBuffer.get() != 0;

        byte[] strBytes = new byte[5];
        byteBuffer.get(strBytes);

        String str = new String(strBytes);

        System.out.println(num1 + ", " + num2 + ", " + ch + ", " + bool + ", " + str);
    }

    /**
     * Automatically called when the PiBot changes status.
     * Don't call this method directly.
     * @param piBotBase The PiBot that changed
     */
    public void onStatusChanged(PiBotBase piBotBase)
    {
        if (!(piBotBase instanceof PiBot))
        {
            return;
        }

        PiBot pibot = (PiBot)piBotBase;

        // Add additional logic as necessary
        System.out.println("New status for pibot " + pibot.getID() + ": " + pibot.getStatus());
    }
}
