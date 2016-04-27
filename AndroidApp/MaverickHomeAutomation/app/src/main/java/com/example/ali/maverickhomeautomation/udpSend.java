package com.example.ali.maverickhomeautomation;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

/**
 * Created by Ali on 4/9/2016.
 */
public class udpSend {
    String messageStr = "";
    int server_port = 2211;

    DatagramSocket s;
    DatagramPacket p;


    public void udpsend(String input_tx) {
        try {
            this.messageStr = input_tx;
            s = new DatagramSocket();
            InetAddress local = InetAddress.getByName("192.168.96.112");
            int msg_length = messageStr.length();
            byte[] message = messageStr.getBytes();
            p = new DatagramPacket(message, msg_length, local, server_port);
            s.send(p);
        } catch (Exception e) {
            e.printStackTrace();
        }


    }

}
