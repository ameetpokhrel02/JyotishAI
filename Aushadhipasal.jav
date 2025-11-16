/**
 * Aushadhipasal - Medicine Store Inventory Management System
 * This program helps manage and display medicine inventory for a local pharmacy
 * 
 * @author Your Name
 * @version 1.0
 */
public class Aushadhipasal {
    
    /**
     * Main method - entry point of the program
     * Displays a formatted inventory report of medicines
     */
    public static void main(String[] args) {
        // TODO: Declare and initialize variables for at least 3 medicines.
        // Include: English name, Nepali name, price per tablet, stock quantity
        
        // Medicine 1
        String medicine1English = "Paracetamol";
        String medicine1Nepali = "प्यारासिटामोल";
        double medicine1Price = 2.50;
        int medicine1Stock = 150;
        boolean medicine1Prescription = false;
        
        // Medicine 2
        String medicine2English = "Amoxicillin";
        String medicine2Nepali = "अमोक्सिसिलिन";
        double medicine2Price = 8.75;
        int medicine2Stock = 80;
        boolean medicine2Prescription = true;
        
        // Medicine 3
        String medicine3English = "Cetirizine";
        String medicine3Nepali = "सेटिरिजिन";
        double medicine3Price = 4.25;
        int medicine3Stock = 120;
        boolean medicine3Prescription = false;
        
        // Medicine 4 (additional medicine)
        String medicine4English = "Vitamin C";
        String medicine4Nepali = "भिटामिन सी";
        double medicine4Price = 3.50;
        int medicine4Stock = 200;
        boolean medicine4Prescription = false;

        // TODO: Print a formatted inventory report header.
        System.out.println("================================================================");
        System.out.println("           AUSHADHI PASAL - MEDICINE INVENTORY REPORT           ");
        System.out.println("================================================================");
        System.out.println("Medicine Name (Nepali Name)        | Price | Stock | Prescription");
        System.out.println("------------------------------------|-------|-------|-------------");
        
        // TODO: Print the details for each medicine in a formatted way.
        printMedicine(medicine1English, medicine1Nepali, medicine1Price, medicine1Stock, medicine1Prescription);
        printMedicine(medicine2English, medicine2Nepali, medicine2Price, medicine2Stock, medicine2Prescription);
        printMedicine(medicine3English, medicine3Nepali, medicine3Price, medicine3Stock, medicine3Prescription);
        printMedicine(medicine4English, medicine4Nepali, medicine4Price, medicine4Stock, medicine4Prescription);
        
        // TODO: Add a footer to the report.
        System.out.println("------------------------------------|-------|-------|-------------");
        System.out.println("Total Medicines: 4");
        System.out.println("Note: Prices are in NPR (Nepalese Rupees) per tablet");
        System.out.println("================================================================");
        System.out.println("Report generated successfully!");
    }
    
    /**
     * Helper method to print formatted medicine information
     * 
     * @param englishName English name of the medicine
     * @param nepaliName Nepali name of the medicine
     * @param price Price per tablet in NPR
     * @param stock Quantity in stock
     * @param prescription Whether prescription is required
     */
    private static void printMedicine(String englishName, String nepaliName, 
                                    double price, int stock, boolean prescription) {
        String prescriptionText = prescription ? "Yes" : "No";
        System.out.printf("%-15s (%-10s) | %5.2f | %5d | %12s%n", 
                         englishName, nepaliName, price, stock, prescriptionText);
    }
}