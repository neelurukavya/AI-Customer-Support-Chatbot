# Procure-to-Pay (Purchasing) in OrbitERP

OrbitERP is a fictional sample ERP product. The process follows common real-world ERP practice.

## What is procure-to-pay?
Procure-to-pay (P2P) is the full buying process: from needing an item to paying the vendor. The steps are purchase requisition, purchase order, goods receipt, vendor invoice and payment.

## What are the steps of procure-to-pay?
1. Purchase requisition: an employee requests an item or service.
2. Approval: the manager approves the requisition.
3. Purchase order: the purchasing team creates an order for a vendor.
4. Goods receipt: the warehouse receives the goods and records them in the system.
5. Vendor invoice: the vendor's bill is entered and checked.
6. Payment: finance pays the vendor after the check passes.

## How do I create a purchase requisition?
Go to Procurement > Requisitions > New. Enter the item, quantity, required date and cost center, then click Submit. It goes to your manager for approval.

## How do I create a purchase order?
Go to Procurement > Purchase Orders > New, or open an approved requisition and click "Create Purchase Order". Select the vendor, check items, prices, tax and delivery date, then click Save and Approve.

## Why does my purchase order need approval?
Approval depends on the order value and the approval rules set by your company. For example, orders above a set amount need a senior manager. The order cannot be sent to the vendor until all approvals are complete.

## What is a goods receipt?
A goods receipt (GRN) records that ordered items arrived at the warehouse. Go to Inventory > Goods Receipt, select the purchase order, enter the received quantity, and click Post. Stock increases and a liability to the vendor is recorded.

## What is three-way matching?
Three-way matching compares three documents before a vendor invoice is paid: the purchase order (what was ordered), the goods receipt (what arrived) and the vendor invoice (what the vendor billed). If quantity, price or amount differ beyond the allowed tolerance, the invoice is blocked for review.

## Why is my vendor invoice blocked?
Common reasons:
- The invoiced quantity is higher than the quantity received.
- The invoice price is different from the purchase order price.
- No goods receipt has been posted yet.
- The invoice is a duplicate of one already entered.
The purchasing team must correct the order or get the vendor to send a corrected invoice.

## How do I enter a vendor invoice?
Go to Finance > Payables > New Invoice. Select the vendor, enter the invoice number and date, and select the matching purchase order. Check that the amounts and taxes match, then click Post.

## How do I pay a vendor?
Go to Finance > Payables > Payment Run. Select the due date and vendors, review the proposed invoices, and click Execute. A payment file for the bank can be exported from the same screen.

## How do I add a new vendor?
Go to Procurement > Vendors > New. Enter the company name, address, tax number, bank details and payment terms. New vendors need approval from finance before they can be used. Bank details are checked to help prevent fraud.

## What are payment terms?
Payment terms say when the vendor must be paid, for example "Net 30" means 30 days after the invoice date. Some terms give a discount for early payment, such as "2/10 Net 30", which means a 2 percent discount if paid within 10 days.
