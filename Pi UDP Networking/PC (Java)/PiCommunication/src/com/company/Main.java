package com.company;

import java.io.IOException;
import java.security.cert.TrustAnchor;
import java.util.Scanner;

import org.omg.PortableInterceptor.SYSTEM_EXCEPTION;
import robobulls.pi.main.*;

public class Main
{
    public static void main(String[] args)
    {
        PiController controller = new PiController();
        controller.start();

        System.out.println("Enter a command (q to exit)");

        Scanner scanner = new Scanner(System.in);

        while (true)
        {
            String currentLine = null;

            try
            {
                if (System.in.available() > 0) // Apparently it returns 0 until enter is pressed
                {
                    currentLine = scanner.nextLine();

                    if (currentLine.equals("q"))
                    {
                        break;
                    }
                }
            }
            catch (IOException e)
            {
                e.printStackTrace();
            }

            controller.update(currentLine);

            try
            {
                Thread.sleep(50);
            }
            catch (InterruptedException e)
            {
                e.printStackTrace();
            }
        }

        controller.stop();
        scanner.close();
    }
}

