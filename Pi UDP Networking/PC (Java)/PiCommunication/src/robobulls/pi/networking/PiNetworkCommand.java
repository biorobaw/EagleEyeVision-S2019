package robobulls.pi.networking;

/**
 * Indicates the type of command that was sent or received
 */
public enum PiNetworkCommand
{
    HEARTBEAT(0),
    SHUTDOWN(1),
    ACK(2),
    USER_MESSAGE(3);

    // The below code is required in order to convert between int and enum
    private final int code;

    PiNetworkCommand(int code)
    {
        this.code = code;
    }

    public int getInt()
    {
        return code;
    }

    public static PiNetworkCommand getEnum(int code)
    {
        return PiNetworkCommand.values()[code];
    }
}
