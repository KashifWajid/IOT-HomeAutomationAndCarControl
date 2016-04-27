package com.example.ali.maverickhomeautomation;

import android.content.Context;
import android.content.DialogInterface;
import android.os.Handler;
import android.os.StrictMode;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.RemoteViews;
import android.widget.ToggleButton;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class MainActivity extends AppCompatActivity {

    Handler mHandler = new Handler();
    String prev_msg;
    String groceryList;
    String[] Glist = {"Dairy\n","Vegetable\n","Fruit\n", "Meat\n",
    "Spices\n","Cleaning\n","Utensils\n","Other1\n","Other2\n","Electronics\n"};
    final Context context = this;
    int counter;
    String ToastMessage;
    char temp = 'F';
    String temp1,temp2,temp3;
    boolean i = true;
    boolean flag = false;
    TextView udp_rex;
    EditText udp_tex;
    String inputText;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);
        setContentView(R.layout.activity_main);


        Button tx_button = (Button) findViewById(R.id.TX);
        Button parkingIn = (Button) findViewById(R.id.park_in);
        Button parkingOut = (Button) findViewById(R.id.park_out);
        Button alarm_off = (Button) findViewById(R.id.alarmoff);
        ToggleButton toggle = (ToggleButton) findViewById(R.id.lighttoggle);

        udp_rex = (TextView) findViewById(R.id.udp_rx);
        udp_tex = (EditText) findViewById(R.id.udp_tx);

        Thread t1 = new Thread(r);
        t1.start();

        Thread t2 = new Thread(Processing);
        t2.start();




        /* Code for sending */
        udp_tex = (EditText) findViewById(R.id.udp_tx);
        tx_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                try{
                    inputText = udp_tex.getText().toString();
                    udpSend SendClient = new udpSend();
                    SendClient.udpsend(inputText);
//                    SendClient.udpsend(inputText);
//                    SendClient.udpsend(inputText);
//                    Toast.makeText(MainActivity.this, "Button Clicked" + inputText,	Toast.LENGTH_SHORT).show();
                }
                catch (Exception e){
                    e.printStackTrace();
                }
            }

        });

        /*Code for Parking In*/
//        Pi ka aik packet
        parkingIn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                udpSend SendClient = new udpSend();
                SendClient.udpsend("PI");
//                SendClient.udpsend("PI");
//                SendClient.udpsend("PI");
            }
        });

        /*Code for Parking Out*/
        parkingOut.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                udpSend SendClient = new udpSend();
                SendClient.udpsend("PO");
//                SendClient.udpsend("PO");
//                SendClient.udpsend("PO");
            }
        });

        /* Alarm Off Code */
        alarm_off.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                udpSend SendClient = new udpSend();
                SendClient.udpsend("A0");
            }
        });

        /* Lights on/Off Code */

        toggle.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    udpSend SendClient = new udpSend();
                    SendClient.udpsend("ON");
                } else {
                    udpSend SendClient = new udpSend();
                    SendClient.udpsend("OFF");
                }
            }
        });
    }
    String msg = "";
    Runnable r = new Runnable() {
        public void run() {
            try {
                DatagramSocket clientsocket=new DatagramSocket(4000);
                byte[] receivedata = new byte[1024];
                while(true)
                {
                    DatagramPacket recv_packet = new DatagramPacket(receivedata, receivedata.length);
                    Log.d("UDP", "S: Receiving...");
                    clientsocket.receive(recv_packet);

                    String rec_str = new String(recv_packet.getData());
                    msg = rec_str;


//                    mHandler.post(setMessage);
                    Log.d(" Received String ", rec_str);
                    InetAddress ipaddress = recv_packet.getAddress();
                    int port = recv_packet.getPort();
                    Log.d("IPAddress : ",ipaddress.toString());
                    Log.d(" Port : ",Integer.toString(port));
                }
            } catch (Exception e) {
                Log.e("UDP", "S: Error", e);
            }
        }
    };

    /* Code for receiving */
    Runnable setMessage = new Runnable() {
        public void run() {
            Toast.makeText(MainActivity.this, ToastMessage,	Toast.LENGTH_SHORT).show();
        }};

    Runnable Processing = new Runnable() {
        @Override
        public void run() {
            while(i){
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }

                if(prev_msg!=msg) {
                    prev_msg=msg;
                    char[] arr = msg.toCharArray();
                    if (msg.length() > 4) {
                        if (arr[0] != temp) {
                            temp = arr[0];
                            if (temp == 'T') {
                                ToastMessage = "Car has been parked In";
                            } else {
                                ToastMessage = "Car has been parked out";
                            }
                            mHandler.post(setMessage);

                        }
                        if (arr[2] != '-' && arr[4] != '-' && arr[6] != '-') {
                            temp1 = Glist[Character.getNumericValue(arr[2])];
                            temp2 = Glist[Character.getNumericValue(arr[4])];
                            temp3 = Glist[Character.getNumericValue(arr[6])];
                            flag = true;

                            arr[2] = '-';
                            arr[4] = '-';
                            arr[6] = '-';


                            Thread t3 = new Thread(GrocerryAlert);
                            t3.start();
                        }
                        if(arr[1]=='A'){
                            ToastMessage = "Emergency/Fire At House";
                            mHandler.post(setMessage);
                        }
                    }
                }

            }
        }
    };

    Runnable GrocerryAlert = new Runnable() {
        public void run() {
            try {
                Thread.sleep(5000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            mHandler.post(GrocerryAlertBox);

        }};

    Runnable GrocerryAlertBox = new Runnable() {
        @Override
        public void run() {
            AlertDialog.Builder alertDialogBuilder = new AlertDialog.Builder(
                    context);
            // set title
            alertDialogBuilder.setTitle("Grocery Alert");
            // set dialog message
            alertDialogBuilder
                    .setMessage("Please Pick the following Groceries: \n" +
                    temp1 + temp2 + temp3)
                    .setCancelable(false)
                    .setPositiveButton("Ok", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int id) {
                            // if this button is clicked, close
                            // current activity

                        }
//                    })
//                    .setNegativeButton("No", new DialogInterface.OnClickListener() {
//                        public void onClick(DialogInterface dialog, int id) {
//                            // if this button is clicked, just close
//                            // the dialog box and do nothing
//                            dialog.cancel();
//                        }
                    });
            // create alert dialog
            AlertDialog alertDialog = alertDialogBuilder.create();
            // show it
            alertDialog.show();

        }

    };
}