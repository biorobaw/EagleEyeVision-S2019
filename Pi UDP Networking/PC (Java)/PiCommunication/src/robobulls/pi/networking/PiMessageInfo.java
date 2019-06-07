package robobulls.pi.networking;

import java.net.DatagramPacket;

/**
 * Stores info about a sent packet.
 */
class PiMessageInfo
{
    DatagramPacket packet;
    long sendTime;
    int packetNum;

    PiMessageInfo(DatagramPacket packet, long sendTime, int packetNum)
    {
        this.packet = packet;
        this.sendTime = sendTime;
        this.packetNum = packetNum;
    }
}
