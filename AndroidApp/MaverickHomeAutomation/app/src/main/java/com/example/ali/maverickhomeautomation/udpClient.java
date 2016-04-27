package com.example.ali.maverickhomeautomation;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.SocketException;

/**
 * Created by Ali on 4/9/2016.
 */
public class udpClient {
    protected String text;
    int server_port = 4000;
    byte[] message = new byte[1500];


    public String udprun() {
        try {
            DatagramSocket s = new DatagramSocket(server_port);//binding socket with port
            DatagramPacket p = new DatagramPacket(message, message.length); // getting the datagram packet
            s.receive(p); // receiving the data
            text = new String(message, 0, p.getLength()); // getting the message and its length
//            s.close();

            /* catching the exceptions */
        } catch (SocketException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "" + text; // Printing out the message sent

    }
}
