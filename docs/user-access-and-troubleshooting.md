# User Access and Troubleshooting in OrbitERP

OrbitERP is a fictional sample ERP product. The practices follow common real-world ERP administration.

## What are user roles?
A role is a set of permissions that decides what a user can see and do. For example, a Sales Clerk can create sales orders but cannot post journal entries. Users get access through roles, not through individual permissions, so rights stay consistent.

## How do I request access to a module?
Raise an access request in the IT service portal. Select the module and role, give a business reason, and submit. Your manager and the module owner must approve before IT grants access. Access is usually given within 2 working days.

## What is segregation of duties?
A control rule that stops one person from doing conflicting tasks. For example, the person who creates a vendor must not also approve payments to that vendor. The ERP blocks role combinations that break these rules.

## I forgot my password
Click "Forgot password" on the login page and enter your username. A reset link is sent to your registered email and is valid for 1 hour. If you do not get it, check spam or ask the IT help desk.

## My account is locked
An account locks after 5 wrong password attempts. It unlocks automatically after 30 minutes, or the IT help desk can unlock it sooner after confirming your identity.

## I get "You are not authorized" for a screen
Your role does not include permission for that screen. Do not share another person's login. Request the access through the IT service portal, or ask your manager which role you need.

## The system is slow
1. Check your internet connection.
2. Close extra browser tabs and refresh the page.
3. Avoid running very large reports during peak hours. Schedule them to run in the background.
4. If it is slow for many users, report it to the IT help desk with the time and screen name.

## A document will not post
Common causes:
- A required field is empty, such as cost center or tax code.
- The posting date is in a closed accounting period.
- Master data is blocked or incomplete.
- A document you depend on, like a goods receipt, is missing.
Read the error message in red at the top of the screen. It usually names the field or rule that failed.

## I see a "duplicate document" warning
The system found a document with the same reference number, vendor or amount. Check whether it was entered already, and do not post it again unless you are sure it is a different transaction.

## How do I cancel or reverse a posted document?
Posted documents cannot be deleted, because the audit trail must stay complete. Use the "Reverse" action, which creates an opposite entry, or issue a credit note. Reversals need a reason and may need approval.

## How do I export a report to Excel?
Run the report, then click Export > Excel. Large exports are prepared in the background and sent to your email.

## How do I contact the IT help desk?
Email erp-support@orbit.example or use the IT service portal. Support is available Monday to Friday, 9 AM to 6 PM IST. Include your username, the screen name, the exact error message and a screenshot.

## What information should I include when reporting a problem?
Your username, company code, the steps you took, the document number if there is one, the exact error message, the date and time, and a screenshot. This helps support fix the issue faster.
