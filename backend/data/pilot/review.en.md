# English translation of the 40 pilot reports

Dataset: `pilot-en-v1`. Source: `tickets.json` (`pilot-pl-v1`).
These are translations of the same cases, not new independent examples.
All labels and translations await human review; no review has been invented.
The data and review decisions are stored in `tickets.en.json`.
Translation provenance and reproduction instructions: `translation-en.md`.

## ACC-01 — accounts_access / low

After I changed my surname, the portal still shows my old account name. Signing in and all permissions work correctly, and I can work normally.

- Category: Account profile information rather than a failure of an application feature.
- Base priority: Only an inconvenience in how the name is displayed.
- Group: `acc-01`; work blocked: `false`.

## ACC-02 — accounts_access / low

Every few days I receive a reminder that my password is about to expire, even though I changed it yesterday. The password works and I can open all the systems I need.

- Category: Notifications about credential validity.
- Base priority: The message does not interfere with work.
- Group: `acc-02`; work blocked: `false`.

## ACC-03 — accounts_access / medium

After I moved to the billing team, the team folder opens in read-only mode. I cannot upload a report, but for now I send it to the person responsible for the folder, who saves the file for me.

- Category: An explicit restriction on permission to write to the folder.
- Base priority: Saving is difficult, but a working workaround is available.
- Group: `acc-folder-access`; work blocked: `false`.

## ACC-04 — accounts_access / medium

Regarding the same permissions issue with the billing folder: I can view documents, but saving results in an access denied message. I send the reports to the person responsible for the folder, who places them there.

- Category: Write access is denied, with no signs of file corruption.
- Base priority: Another person can save the file on the user's behalf.
- Group: `acc-folder-access`; work blocked: `false`.

## ACC-05 — accounts_access / medium

My new phone does not receive email sign-in confirmations. I currently sign in using a code from a backup key and can receive messages, but I would like to restore confirmations on the phone.

- Category: A problem with the second authentication factor.
- Base priority: The backup key allows work to continue.
- Group: `acc-05`; work blocked: `false`.

## ACC-06 — accounts_access / medium

The application rejects my login with a message saying that my password has expired. Changing it myself in the portal works and restores access, but the password expires again the next day.

- Category: The password validity cycle and account access.
- Base priority: Changing the password independently restores access.
- Group: `acc-06`; work blocked: `false`.

## ACC-07 — accounts_access / high

My account for the warehouse system has been locked. I cannot receive today's delivery; I have no second account and no way to complete this task outside the system.

- Category: An explicit account lock.
- Base priority: An important task for one person is blocked with no workaround.
- Group: `acc-07`; work blocked: `true`.

## ACC-08 — accounts_access / high

When signing in to the VPN, I see this message: the user does not have permission for remote connections. I cannot complete an urgent billing task from home, and access is available only through this VPN.

- Category: The VPN explicitly denies permission rather than reporting a connection failure.
- Base priority: An essential task cannot be accessed and no workaround is available.
- Group: `acc-08`; work blocked: `true`.

## ACC-09 — accounts_access / high

After I changed positions, I lost permission to approve invoices. The system displays an insufficient permissions message, and I must approve payments today; no other authorized person is on this shift.

- Category: The role required to perform the operation is missing.
- Base priority: Payment approval is blocked with no authorized replacement.
- Group: `acc-09`; work blocked: `true`.

## ACC-10 — accounts_access / critical

Since this morning, all employees in the customer service center have received a message at sign-in saying their accounts are disabled. The entire department cannot serve customers; no backup account is available.

- Category: The accounts of multiple users are explicitly disabled.
- Base priority: A key process for the entire department is unavailable.
- Group: `acc-10`; work blocked: `true`.

## HW-01 — hardware / low

A single bright dot has appeared near the bottom edge of my external monitor and stays lit. The rest of the image is readable and I can perform all my tasks normally.

- Category: A physical symptom on the display.
- Base priority: A minor defect that does not limit work.
- Group: `hw-01`; work blocked: `false`.

## HW-02 — hardware / low

The fan in my computer has started running more loudly. The device does not shut down, there are no temperature warnings, and I can perform all my tasks.

- Category: A symptom involving the operation of a physical component.
- Base priority: The noise is an inconvenience without blocking tasks.
- Group: `hw-02`; work blocked: `false`.

## HW-03 — hardware / medium

The printer at reception jams paper even when I start a test page from its own control panel. I am currently printing documents on the device in the next room.

- Category: The jam occurs independently of the application and connection.
- Base priority: Another printer provides a working workaround.
- Group: `hw-reception-printer`; work blocked: `false`.

## HW-04 — hardware / medium

The same reception printer is once again stopping a sheet halfway through, including during its own test. I use the printer in the next room and can issue documents.

- Category: The physical paper feed mechanism.
- Base priority: Printing on another device allows work to continue.
- Group: `hw-reception-printer`; work blocked: `false`.

## HW-05 — hardware / medium

Several keys on my laptop's built-in keyboard do not respond. I connected a USB keyboard and can type, but this makes working in meeting rooms more difficult.

- Category: Nonfunctional keys on the device.
- Base priority: An external keyboard allows work to continue.
- Group: `hw-05`; work blocked: `false`.

## HW-06 — hardware / medium

The laptop camera shows a black image even in the operating system's device test. For meetings, I use a borrowed USB camera that works correctly.

- Category: The device symptom is confirmed outside the meeting application.
- Base priority: A borrowed camera provides a working replacement.
- Group: `hw-06`; work blocked: `false`.

## HW-07 — hardware / high

The computer does not start when I press the button, and no indicator lights come on despite being plugged into a working power socket. This is my only workstation for handling orders and no replacement computer is available.

- Category: The device has no power or does not respond.
- Base priority: An important task for one person has no replacement setup.
- Group: `hw-07`; work blocked: `true`.

## HW-08 — hardware / high

The barcode scanner at my workstation does not turn on and still does not respond when connected to a different port. I cannot register parcels; the program does not allow codes to be entered manually and we have no spare scanner.

- Category: A physical device does not respond.
- Base priority: Registering parcels is impossible with no workaround.
- Group: `hw-08`; work blocked: `true`.

## HW-09 — hardware / high

My laptop's power adapter has stopped charging it, and the battery is now empty. I must prepare payroll on this device today; no other adapter or workstation with this access is available.

- Category: A nonfunctional power adapter and a discharged device.
- Base priority: An essential task is blocked by the lack of replacement equipment.
- Group: `hw-09`; work blocked: `true`.

## HW-10 — hardware / critical

The main disk array will not turn on, and the indicator lights on both power supplies are off. All teams have lost access to files needed to process orders and no working copy is available.

- Category: Physical signs that the disk array has no power.
- Base priority: The failure of essential equipment blocks multiple teams.
- Group: `hw-10`; work blocked: `true`.

## NET-01 — network / low

After my laptop wakes from sleep, the connection to the company Wi-Fi appears only after a few seconds. It then works reliably; this does not interrupt tasks and I can use all tools normally.

- Category: A short delay in establishing the wireless connection.
- Base priority: A minor delay that does not block required tasks.
- Group: `net-01`; work blocked: `false`.

## NET-02 — network / low

The company Wi-Fi signal in the break room is weak and pages load slowly. We do not perform work tasks there; the connection works correctly at our desks and work is not affected.

- Category: A weak wireless signal in a specific location.
- Base priority: An inconvenience outside the place where work is performed.
- Group: `net-02`; work blocked: `false`.

## NET-03 — network / medium

In meeting room B, the Wi-Fi connection drops every few minutes. After I connect the laptop by cable to the network socket in that room, online meetings work reliably.

- Category: The wireless connection drops.
- Base priority: A wired connection provides a working workaround.
- Group: `net-meeting-room-b`; work blocked: `false`.

## NET-04 — network / medium

I am reporting the same company wireless network disconnections in room B. I can continue the call over a cable; after I unplug it, the Wi-Fi loses its connection again.

- Category: The symptom concerns a particular Wi-Fi connection.
- Base priority: The cable allows the meeting to continue.
- Group: `net-meeting-room-b`; work blocked: `false`.

## NET-05 — network / medium

My home internet drops my connection to the company several times a day, including during ordinary web browsing. I switch the laptop to my phone's internet connection and can then work reliably.

- Category: The connection is lost outside a single application as well.
- Base priority: The phone's internet connection allows work to continue.
- Group: `net-05`; work blocked: `false`.

## NET-06 — network / medium

The network socket in room 12 provides no connection, while the same laptop with the same cable connects in the next room. I am temporarily using the company Wi-Fi to handle my tasks.

- Category: A problem with the connection path through a specific socket.
- Base priority: Working Wi-Fi provides a workaround.
- Group: `net-06`; work blocked: `false`.

## NET-07 — network / high

The VPN accepts my password and sign-in confirmation, but setting up the tunnel times out. Internet access outside the VPN works; I cannot connect to the system needed for today's dispatch and have no other way to access it.

- Category: Authentication works, but the connection cannot be established.
- Base priority: An important task for one person is blocked with no workaround.
- Group: `net-07`; work blocked: `true`.

## NET-08 — network / high

At my workstation, neither the wired connection nor Wi-Fi can access the company network. I cannot process orders, and there is no replacement workstation or mobile internet coverage here.

- Category: Two types of connection cannot access the network.
- Base priority: Order processing is blocked and there is no alternative.
- Group: `net-08`; work blocked: `true`.

## NET-09 — network / high

During a remote session with the server, the connection drops every few dozen seconds. Other services over this link are also affected; I must finish a data import today and have no other connection or on-site access.

- Category: Connectivity is lost to multiple services, without guessing the cause.
- Base priority: An urgent task has no working alternative access path.
- Group: `net-09`; work blocked: `true`.

## NET-10 — network / critical

Internet access and connections to headquarters have stopped working throughout the branch, over both cable and Wi-Fi. Thirty people cannot take orders, and the backup link also provides no access.

- Category: A widespread loss of network connectivity.
- Base priority: Essential order processing for multiple people is blocked.
- Group: `net-10`; work blocked: `true`.

## SW-01 — software / low

After the editor update, some icons on the toolbar have blurred edges. All buttons work, documents save correctly, and I can work as before.

- Category: Application elements are displayed incorrectly.
- Base priority: A purely cosmetic interface problem.
- Group: `sw-01`; work blocked: `false`.

## SW-02 — software / low

The list of recently opened documents in the program does not retain the selected order after a restart. Documents open normally and the sorting is not needed to perform tasks.

- Category: The application fails to remember a setting.
- Base priority: A minor inconvenience without losing a required feature.
- Group: `sw-02`; work blocked: `false`.

## SW-03 — software / medium

The reporting program closes when exporting to PDF. I can open the same reports in the browser and save them to PDF using print, so I send them on time.

- Category: A specific program feature fails.
- Base priority: An alternative way to create a PDF works.
- Group: `sw-reports-pdf`; work blocked: `false`.

## SW-04 — software / medium

I am following up on the same report export error: clicking save as PDF shuts down the application. I still prepare the files by printing from the browser version and can deliver the reports.

- Category: A recurrence of the export failure rather than a printer problem.
- Base priority: The browser version allows the task to be completed.
- Group: `sw-reports-pdf`; work blocked: `false`.

## SW-05 — software / medium

In one program, printing a form causes the window to close. The printer's test page works; I can export the form as an image and print it from another program.

- Category: The error affects the application while the printer works.
- Base priority: Another program allows printing.
- Group: `sw-05`; work blocked: `false`.

## SW-06 — software / medium

The calendar in the desktop application does not show newly added meetings, although they are visible in its web version. I check the schedule in the browser and do not miss meetings.

- Category: An outdated view in a particular version of the application.
- Base priority: The web version provides access to the schedule.
- Group: `sw-06`; work blocked: `false`.

## SW-07 — software / high

The accounting program closes every time I approve a declaration. Other features work, but I must submit the declaration today; there is no web version or other way to approve it.

- Category: A repeatable failure of an operation in the application.
- Base priority: An important operation is impossible with no workaround.
- Group: `sw-07`; work blocked: `true`.

## SW-08 — software / high

After an update, the document signing application will not start and immediately displays a program error. I must sign a contract today, and company procedure permits only this application with no alternative.

- Category: The program will not start after an update.
- Base priority: Signing a required contract is blocked.
- Group: `sw-08`; work blocked: `true`.

## SW-09 — software / high

In the warehouse system, approving my dispatch list consistently returns a calculation error. I have the required permissions and other lists open correctly, but this dispatch cannot be approved manually or in another tool.

- Category: A calculation error in a feature rather than access being denied.
- Base priority: A specific important task has no workaround.
- Group: `sw-09`; work blocked: `true`.

## SW-10 — software / critical

After a new version was deployed, the order system ends the session with a program error whenever anyone tries to save an order. All customer service agents are affected; the entire sales operation is at a standstill and there is no fallback mode.

- Category: The application's save feature fails for multiple users.
- Base priority: An essential service for the entire team is unavailable.
- Group: `sw-10`; work blocked: `true`.

---

# Expansion to 120 reports — 2026-11-01

The user approved the original 40 examples and their labels in the conversation. The `pending` description above is historical.
The 80 new proposals below await human review. The dataset contains 30 examples per category.
Current decisions are in `tickets.en.json`: 40 approved and 80 pending.

## ACC-11 — accounts_access / low

My account's entry in the address book shows my old extension number. I can sign in and use every service; the incorrect number does not interfere with my tasks.

- Category: Outdated information in the account profile.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `acc-11`; work_blocked: `false`; review: `pending`.

## ACC-12 — accounts_access / low

The self-service portal still shows my previous team name, even though I moved a month ago. I already have access to the new team, and the displayed name does not block anything.

- Category: Organizational information attached to the account.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `acc-12`; work_blocked: `false`; review: `pending`.

## ACC-13 — accounts_access / low

When signing in, I see an old role from a completed project in the list. Selecting it opens nothing, but my current role provides all necessary permissions and I can work normally.

- Category: An outdated user role remains visible.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `acc-13`; work_blocked: `false`; review: `pending`.

## ACC-14 — accounts_access / low

The account panel displays a message asking me to add a profile photo. I do not want to add one; I can dismiss the message and all tools remain available.

- Category: A requirement concerning the account profile.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `acc-14`; work_blocked: `false`; review: `pending`.

## ACC-15 — accounts_access / medium

I have lost permission to create new documents in the Orion project folder, although I can read existing ones. A teammate saves the files I send her, so work continues.

- Category: Permission to create documents in a folder is missing.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `acc-orion-folder`; work_blocked: `false`; review: `pending`.

## ACC-16 — accounts_access / medium

This concerns the same write access denial in the Orion directory: reading works, but adding a file produces an insufficient permissions message. I pass the documents to a colleague who places them in the directory.

- Category: An explicit denial of write permission.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `acc-orion-folder`; work_blocked: `false`; review: `pending`.

## ACC-17 — accounts_access / medium

After replacing my phone, the authenticator app does not contain my company account and I cannot approve sign-ins with it. Saved recovery codes let me access the systems and complete my tasks.

- Category: An authentication factor has not been configured.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `acc-17`; work_blocked: `false`; review: `pending`.

## ACC-18 — accounts_access / medium

Single sign-on to the portal says my account is not assigned to this application. Signing in directly with a local account still works and I can handle my tasks.

- Category: The account is not assigned to the application.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `acc-18`; work_blocked: `false`; review: `pending`.

## ACC-19 — accounts_access / medium

Trying to set a new password myself produces a message saying I am not allowed to change it. My existing password still works and I can use email and the other systems.

- Category: Permission to change the password is denied.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `acc-19`; work_blocked: `false`; review: `pending`.

## ACC-20 — accounts_access / medium

In the ticketing tool, my role allows me to read cases, but permission to add notes has been removed. I send notes to the duty operator, who records them; customer service can continue.

- Category: A specific role permission is missing.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `acc-20`; work_blocked: `false`; review: `pending`.

## ACC-21 — accounts_access / medium

The portal rejects sign-in with my security key, saying the key is not assigned to my user. I can select a second registered key and access the tools.

- Category: The security key is not linked to the account.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `acc-21`; work_blocked: `false`; review: `pending`.

## ACC-22 — accounts_access / medium

I cannot see the archived reports because the system explicitly says I am not a member of the access group. The project lead shares the reports I need individually, so I can prepare the summary.

- Category: Membership in an access group is missing.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `acc-22`; work_blocked: `false`; review: `pending`.

## ACC-23 — accounts_access / high

While signing the payment list, the system says my role does not permit payment approval. I am the only authorized person on duty, and without this operation I cannot send today's payments.

- Category: Permission to approve payments is denied.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `acc-23`; work_blocked: `true`; review: `pending`.

## ACC-24 — accounts_access / high

When accessing the project repository, I receive a message saying my organization membership has expired. I must deliver a fix to the customer today and have neither a copy of the code nor another authorized account.

- Category: Membership required for access has expired.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `acc-24`; work_blocked: `true`; review: `pending`.

## ACC-25 — accounts_access / high

My device administrator account has been disabled, as confirmed by the sign-in screen. I must configure a new employee's workstation today; my other account lacks those permissions and no replacement administrator is available.

- Category: A privileged account is explicitly disabled.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `acc-25`; work_blocked: `true`; review: `pending`.

## ACC-26 — accounts_access / high

The document management system requires a second factor, but my only registered key has been lost. I have no recovery codes or other method and cannot send the documentation required today.

- Category: No authentication factor is available.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `acc-26`; work_blocked: `true`; review: `pending`.

## ACC-27 — accounts_access / high

After my responsibilities changed, access to the month-end folder was denied with an insufficient permissions message. I need these documents for today's settlement; nobody on this shift can provide them.

- Category: Access to a required folder is denied.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `acc-month-end-folder`; work_blocked: `true`; review: `pending`.

## ACC-28 — accounts_access / high

I am reporting again the loss of permission to the same month-end directory. I cannot read the documents needed for today's settlement, and nobody available has permission to share a copy with me.

- Category: A repeated report of explicit missing folder permissions.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `acc-month-end-folder`; work_blocked: `true`; review: `pending`.

## ACC-29 — accounts_access / critical

All dispatchers see a message at sign-in to the transport system saying the operator role has been revoked. We cannot issue assignments to drivers, and no account on this shift has alternative access.

- Category: The operator role has been revoked for multiple users.
- Base priority: An unavailable essential service blocks multiple people with no fallback mode.
- Group: `acc-29`; work_blocked: `true`; review: `pending`.

## ACC-30 — accounts_access / critical

Since this morning, the authentication system has rejected the accounts of the entire patient service team as inactive. Appointment registration has stopped for everyone, and emergency sign-in is not permitted either.

- Category: Multiple accounts are blocked as inactive.
- Base priority: An unavailable essential service blocks multiple people with no fallback mode.
- Group: `acc-30`; work_blocked: `true`; review: `pending`.

## HW-11 — hardware / low

A plastic hinge cover on my work laptop's case has cracked. The screen opens steadily, no wires are exposed, and I can perform all my tasks without restrictions.

- Category: Damage to a physical part of the case.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `hw-11`; work_blocked: `false`; review: `pending`.

## HW-12 — hardware / low

The volume wheel on my headset is loose, but the sound and microphone work. I adjust the volume in the operating system and can make calls without difficulty.

- Category: A mechanical defect in a headset component.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `hw-12`; work_blocked: `false`; review: `pending`.

## HW-13 — hardware / low

The Caps Lock indicator on my external keyboard has stopped lighting up. The keys themselves work, I can see the state on screen, and writing documents is not affected.

- Category: A device indicator is not working.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `hw-13`; work_blocked: `false`; review: `pending`.

## HW-14 — hardware / low

The monitor stand does not hold the selected height and slides to its lowest position. The screen is readable for me at that height and I can perform all my duties.

- Category: The height adjustment mechanism of the monitor stand.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `hw-14`; work_blocked: `false`; review: `pending`.

## HW-15 — hardware / medium

The card reader in terminal number 4 does not respond even in its own diagnostic test. I moved to the available terminal number 5 and can still serve customers.

- Category: A faulty reader confirmed by the device test.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `hw-terminal-4-reader`; work_blocked: `false`; review: `pending`.

## HW-16 — hardware / medium

I am following up on the same reader in terminal 4: cards are not detected even in the terminal diagnostics. I use the neighboring workstation 5, so customers can be served.

- Category: A repeated report of the faulty physical reader.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `hw-terminal-4-reader`; work_blocked: `false`; review: `pending`.

## HW-17 — hardware / medium

One USB port on the docking station does not recognize connected devices, regardless of the cable. The other ports work; I moved the mouse and keyboard to them and can work.

- Category: A specific device port is faulty.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `hw-17`; work_blocked: `false`; review: `pending`.

## HW-18 — hardware / medium

The mobile terminal's battery does not hold a charge and the device shuts off when unplugged. I work at the counter with the power connected and can record outgoing items.

- Category: The battery cannot maintain power.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `hw-18`; work_blocked: `false`; review: `pending`.

## HW-19 — hardware / medium

The mouse registers a single click twice, including on another computer. I borrowed a working spare mouse and can complete my tasks, but mine needs replacement.

- Category: The physical device shows the same symptom on another computer.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `hw-19`; work_blocked: `false`; review: `pending`.

## HW-20 — hardware / medium

The document scanner's feeder stops sheets even when copying without a computer. I can scan individual pages from the glass and send the documents that way.

- Category: The paper feeding mechanism is malfunctioning.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `hw-20`; work_blocked: `false`; review: `pending`.

## HW-21 — hardware / medium

The external drive is not detected on two computers and its indicator does not light up. The files I need are also on the company file share, so I retrieve them there and continue working.

- Category: The device does not respond on different computers.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `hw-21`; work_blocked: `false`; review: `pending`.

## HW-22 — hardware / medium

The laptop's built-in microphone crackles even in a local test recording. A connected headset records clearly and I use it for all calls.

- Category: The microphone symptom occurs outside the calling application.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `hw-22`; work_blocked: `false`; review: `pending`.

## HW-23 — hardware / high

The only monitor at the inspection workstation has its backlight on but does not display even its own menu. I must inspect a batch today; we have no other screen or workstation for this inspection.

- Category: The monitor cannot display even its own menu.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `hw-23`; work_blocked: `true`; review: `pending`.

## HW-24 — hardware / high

The shipping label printer does not feed paper and reports a mechanism fault even in the control panel test. Today's parcels cannot be dispatched without these labels, and there is no second printer or alternative printout.

- Category: A printer mechanism failure confirmed without the application.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `hw-24`; work_blocked: `true`; review: `pending`.

## HW-25 — hardware / high

The signature capture device will not turn on through any available port. I must collect a customer's signature today, the procedure does not permit paper, and we have no spare device.

- Category: The physical device does not power on.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `hw-25`; work_blocked: `true`; review: `pending`.

## HW-26 — hardware / high

The computer used to prepare presentations has a clicking drive, and the hardware test reports a drive failure while the system will not start. The required files are only here; I have no backup or other way to prepare today's demonstration.

- Category: A drive failure reported by the hardware test.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `hw-26`; work_blocked: `true`; review: `pending`.

## HW-27 — hardware / high

The only charger for the terminal at the loading gate has a broken cable, and the terminal is discharged. I must register vehicles now, but there is no second charger or other workstation with this function.

- Category: A damaged charger cable leaves the terminal without power.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `hw-loading-gate-charger`; work_blocked: `true`; review: `pending`.

## HW-28 — hardware / high

I am reporting again the same severed charger cable for the terminal at the gate. The device has no battery power left, so I cannot enter arriving vehicles; we have neither a replacement charger nor another workstation.

- Category: A repeated report of the terminal charger damage.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `hw-loading-gate-charger`; work_blocked: `true`; review: `pending`.

## HW-29 — hardware / critical

The central UPS supplies no output voltage and shows a power module fault even after its self-test. All service point workstations are off, customers cannot be served, and no alternative power supply is available.

- Category: A fault in a physical power supply module.
- Base priority: An unavailable essential service blocks multiple people with no fallback mode.
- Group: `hw-29`; work_blocked: `true`; review: `pending`.

## HW-30 — hardware / critical

The main registration server does not respond to the power button, and both power supply units show red indicators. The entire team cannot handle appointments, and no working replacement server is available.

- Category: Hardware symptoms of a server power failure.
- Base priority: An unavailable essential service blocks multiple people with no fallback mode.
- Group: `hw-30`; work_blocked: `true`; review: `pending`.

## NET-11 — network / low

When I move between rooms, my work phone briefly shows no Wi-Fi network and then reconnects by itself. I am not making calls or performing tasks during that time, and I do not lose access to tools needed for work.

- Category: A brief interruption while moving between access points.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `net-11`; work_blocked: `false`; review: `pending`.

## NET-12 — network / low

The guest network in the waiting area opens its welcome page with a delay of a few seconds. The work network at the desks operates normally, and the delay does not affect work tasks.

- Category: A delay in establishing access to the guest network.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `net-12`; work_blocked: `false`; review: `pending`.

## NET-13 — network / low

After I plug in the cable, the network icon changes to connected only after a few seconds. All services then work reliably, and the wait does not interrupt any task.

- Category: A delay in establishing the wired connection.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `net-13`; work_blocked: `false`; review: `pending`.

## NET-14 — network / low

The company Wi-Fi has very weak coverage on the office terrace and pages load slowly. This is a break area; I have full access in the work rooms and can perform all my duties.

- Category: Weak network coverage in a specific area.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `net-14`; work_blocked: `false`; review: `pending`.

## NET-15 — network / medium

In training room C, the wired connection drops every few minutes, including during ordinary web browsing. I switched the computer to Wi-Fi and the training can continue.

- Category: Repeated disconnections of the wired connection.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `net-training-room-c`; work_blocked: `false`; review: `pending`.

## NET-16 — network / medium

This is another report of the wired network dropping in room C: services stop responding and return after a while. The training works without interruptions over wireless, so we are currently using it.

- Category: The same connection stability problem in the room.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `net-training-room-c`; work_blocked: `false`; review: `pending`.

## NET-17 — network / medium

In the office, no websites open by name, but accessing the server's known IP address works. After switching to an approved backup resolver, names work again and I can handle my tasks.

- Category: A name resolution problem on the network connection.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `net-17`; work_blocked: `false`; review: `pending`.

## NET-18 — network / medium

During calls over the company connection, the audio cuts out, and a test shows packet loss to other services as well. After connecting to the backup link, I can make calls and serve customers.

- Category: Packet loss affects multiple services.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `net-18`; work_blocked: `false`; review: `pending`.

## NET-19 — network / medium

The company wireless network does not assign my laptop an address; the device shows that it is waiting for network configuration. Connecting by cable gives me access and I can work.

- Category: The wireless connection does not receive an address configuration.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `net-19`; work_blocked: `false`; review: `pending`.

## NET-20 — network / medium

After I sign in to the VPN, the connection disappears when sending a larger file, and the same happens with several services. I transfer files through an approved external portal and the task can be completed.

- Category: The VPN connection is unstable after authentication.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `net-20`; work_blocked: `false`; review: `pending`.

## NET-21 — network / medium

The rented work room has no working connection to company headquarters, although local websites are reachable. I use an approved mobile connection and can perform my duties that way.

- Category: The connection route to headquarters is unavailable.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `net-21`; work_blocked: `false`; review: `pending`.

## NET-22 — network / medium

After moving desks, the connection through socket 18 is very slow when copying files and opening different services. I moved to an available desk with another socket and work proceeds normally.

- Category: A specific network connection has limited performance.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `net-22`; work_blocked: `false`; review: `pending`.

## NET-23 — network / high

My service point cannot connect to headquarters; requests to all its services time out. I must confirm outgoing items today, and there is no backup link or possibility of moving to another workstation.

- Category: Connectivity to multiple headquarters services is unavailable.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `net-23`; work_blocked: `true`; review: `pending`.

## NET-24 — network / high

Neither the company wired nor wireless network works on my work laptop; I cannot reach any company address. I must conduct a customer call today, my phone has no coverage here, and I have no other workstation.

- Category: Different connections cannot access the network.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `net-24`; work_blocked: `true`; review: `pending`.

## NET-25 — network / high

The remote desktop connection authenticates, but traffic to the server stalls and times out, as does access to other services at that location. I must approve today's import and have no other route to the server.

- Category: Connectivity to the location is missing after authentication.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `net-25`; work_blocked: `true`; review: `pending`.

## NET-26 — network / high

The connection used to broadcast today's training loses packets and disconnects other applications as well. I cannot deliver the broadcast, and the devices available here do not support any other connection.

- Category: Loss of connectivity affects multiple applications.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `net-26`; work_blocked: `true`; review: `pending`.

## NET-27 — network / high

My connection to the company from the field office has stopped responding; all headquarters services time out, although signing in to the local device works. I must send a report today, and this location has no alternative link or access point.

- Category: Connectivity to headquarters is lost from one field office.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `net-field-office-uplink`; work_blocked: `true`; review: `pending`.

## NET-28 — network / high

I am following up on the unavailable field office connection to headquarters. Every headquarters service times out; today's report is waiting, and there is no backup network or second access route here.

- Category: The same loss of connectivity to headquarters services.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `net-field-office-uplink`; work_blocked: `true`; review: `pending`.

## NET-29 — network / critical

Internal system names have stopped resolving throughout the company, while known IP addresses remain reachable. All teams have lost access to order processing, the backup resolver also fails to respond, and there is no approved workaround.

- Category: A shared network name resolution outage.
- Base priority: An unavailable essential service blocks multiple people with no fallback mode.
- Group: `net-29`; work_blocked: `true`; review: `pending`.

## NET-30 — network / critical

Both network routes between the warehouse and headquarters are unavailable; every central service times out. All warehouse shifts have stopped because outgoing items cannot be recorded, and there is no third link or offline mode.

- Category: Connectivity is unavailable through both available routes.
- Base priority: An unavailable essential service blocks multiple people with no fallback mode.
- Group: `net-30`; work_blocked: `true`; review: `pending`.

## SW-11 — software / low

In the note-taking program, tooltip text overlaps an icon after the latest update. The tooltip disappears when I move the mouse away, all features work, and I can write notes normally.

- Category: A program element is displayed incorrectly.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `sw-11`; work_blocked: `false`; review: `pending`.

## SW-12 — software / low

The application shows the month name in English even though I selected Polish. The dates are correct, I understand the names, and I can perform every operation.

- Category: The application interface is not localized correctly.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `sw-12`; work_blocked: `false`; review: `pending`.

## SW-13 — software / low

In the program's help window, the table of contents link scrolls to the wrong heading. All other features work and I do not need this help for my current duties.

- Category: A link in the application behaves incorrectly.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `sw-13`; work_blocked: `false`; review: `pending`.

## SW-14 — software / low

After restarting the tool, the selected theme color returns to the default. I do not lose settings needed for my tasks or any documents and can work without difficulty.

- Category: The program does not remember a cosmetic setting.
- Base priority: A minor inconvenience without restricting required tasks.
- Group: `sw-14`; work_blocked: `false`; review: `pending`.

## SW-15 — software / medium

Exporting the contact list to CSV in the sales application ends with a program error. I can copy the table into a spreadsheet and save it as CSV, so I deliver the lists on time.

- Category: The application's export feature fails.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `sw-contacts-csv`; work_blocked: `false`; review: `pending`.

## SW-16 — software / medium

I am reporting the same contact CSV saving error again: the export button displays an exception instead of producing a file. Copying the table to a spreadsheet and saving it there still lets me prepare the list.

- Category: A repeated report of the contact export error.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `sw-contacts-csv`; work_blocked: `false`; review: `pending`.

## SW-17 — software / medium

The date filter in the reporting program shows an empty list despite existing records. I disable the filter and select the required rows from the full list, so I can prepare the report.

- Category: The program filters results incorrectly.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `sw-17`; work_blocked: `false`; review: `pending`.

## SW-18 — software / medium

The invoicing program sorts invoice numbers incorrectly and puts documents in a random order. Searching for a specific number works, so I can still issue and find invoices.

- Category: The document sorting feature is incorrect.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `sw-18`; work_blocked: `false`; review: `pending`.

## SW-19 — software / medium

The PDF attachment preview in the application shows a blank page, but the downloaded file opens correctly in a separate reader. I download the documents and use them to handle cases.

- Category: The application file preview is faulty.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `sw-19`; work_blocked: `false`; review: `pending`.

## SW-20 — software / medium

Dragging an attachment into the form closes the window with a program error. Adding the same file through the file selection button works, so I can submit the required forms.

- Category: One method of adding attachments fails.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `sw-20`; work_blocked: `false`; review: `pending`.

## SW-21 — software / medium

In the summary program, the column total does not update after a row changes. Reopening the document recalculates it correctly; I check the values that way and complete the summaries.

- Category: The application does not refresh calculations correctly.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `sw-21`; work_blocked: `false`; review: `pending`.

## SW-22 — software / medium

The time tracking application freezes on the save screen, although its browser version works. I enter hours through the browser and can account for my work.

- Category: A particular version of the application freezes.
- Base priority: The report describes a working workaround that allows work to continue.
- Group: `sw-22`; work_blocked: `false`; review: `pending`.

## SW-23 — software / high

The payroll program displays an arithmetic error while calculating my summary and stops the operation. I must finalize salaries today, but they cannot be approved manually or in another tool.

- Category: A calculation error interrupts a program feature.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `sw-23`; work_blocked: `true`; review: `pending`.

## SW-24 — software / high

When saving a prepared quotation, the sales application consistently displays an exception and removes the form. I must send this quotation today, company policy requires it to be saved in this system, and no alternative version is available.

- Category: A repeatable form saving error.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `sw-24`; work_blocked: `true`; review: `pending`.

## SW-25 — software / high

The data import tool stops on every file with a parsing error, including its own valid sample file. I must load the customer's data today and there is no manual import or other tool.

- Category: The import tool's parser fails.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `sw-25`; work_blocked: `true`; review: `pending`.

## SW-26 — software / high

The design application closes while opening my required document, including its saved copy. I have the correct permissions, but cannot prepare today's documentation, and no other program supports this format.

- Category: The application closes while reading a document.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `sw-26`; work_blocked: `true`; review: `pending`.

## SW-27 — software / high

Publishing my schedule in the duty roster system ends with a program error despite successful data validation. I must share tomorrow's schedule, but the system has no second publication method and exports are not accepted.

- Category: The publication operation fails after data validation.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `sw-roster-publication`; work_blocked: `true`; review: `pending`.

## SW-28 — software / high

This is a follow-up on the same schedule: form validation passes, but confirming publication displays an exception. Tomorrow's schedule is still unavailable; there is no other publication path and an export cannot replace it.

- Category: The same schedule publication error.
- Base priority: The reporter's important task is blocked and no workaround is available.
- Group: `sw-roster-publication`; work_blocked: `true`; review: `pending`.

## SW-29 — software / critical

After the warehouse application update, saving any outgoing item ends with an exception for every operator. Sign-in and the network work, but the entire warehouse cannot release goods and there is no offline mode or replacement system.

- Category: The application's save feature fails for every operator.
- Base priority: An unavailable essential service blocks multiple people with no fallback mode.
- Group: `sw-29`; work_blocked: `true`; review: `pending`.

## SW-30 — software / critical

The call center program closes at every workstation when accepting a call, while other network services work. The entire team cannot take customer calls and we have no alternative application or call forwarding.

- Category: The application closes when performing a shared operation.
- Base priority: An unavailable essential service blocks multiple people with no fallback mode.
- Group: `sw-30`; work_blocked: `true`; review: `pending`.

---

# Final pilot batch — 50 poorly described reports

The user also approved the preceding 80 pairs. All previous 120 examples are now approved.
The 50 new proposals below remain pending. They are only queries against the 120 KNN references, not reference examples.
Null labels mean the description contains insufficient information. They must not be guessed or replaced with medium.

## WEAK-01 — accounts_access / null

Account locked.

- Category: The description identifies an account, permission, or authentication issue.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-02 — accounts_access / null

I don't have permission for the folder.

- Category: The description identifies an account, permission, or authentication issue.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-03 — accounts_access / null

MFA isn't coming through to my phone.

- Category: The description identifies an account, permission, or authentication issue.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-04 — accounts_access / null

Password expired, can't sign in.

- Category: The description identifies an account, permission, or authentication issue.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-05 — accounts_access / null

My role in the system has been removed.

- Category: The description identifies an account, permission, or authentication issue.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-06 — accounts_access / null

Can't approve the sign-in on my new phone.

- Category: The description identifies an account, permission, or authentication issue.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-07 — accounts_access / low

My account shows my old phone number. I can work normally.

- Category: The description identifies an account, permission, or authentication issue.
- Base priority: The description confirms that work can continue normally despite the inconvenience.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-08 — accounts_access / medium

No permission to access reports. A colleague sends me the files.

- Category: The description identifies an account, permission, or authentication issue.
- Base priority: The description includes an available working workaround.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-09 — hardware / null

A key has broken off.

- Category: The description contains a physical symptom involving a device.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-10 — hardware / null

The monitor's display panel is cracked.

- Category: The description contains a physical symptom involving a device.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-11 — hardware / null

The fan is scraping against the case.

- Category: The description contains a physical symptom involving a device.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-12 — hardware / null

The battery is swollen.

- Category: The description contains a physical symptom involving a device.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-13 — hardware / null

The power adapter is sparking.

- Category: The description contains a physical symptom involving a device.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-14 — hardware / low

The monitor stand cracked. The screen is stable, I can work.

- Category: The description contains a physical symptom involving a device.
- Base priority: The description confirms that work can continue normally despite the inconvenience.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-15 — hardware / medium

The mouse doesn't click, a borrowed one works.

- Category: The description contains a physical symptom involving a device.
- Base priority: The description includes an available working workaround.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-16 — hardware / high

The only scanner won't turn on. Parcels are waiting, no spare available.

- Category: The description contains a physical symptom involving a device.
- Base priority: An important task is blocked with no available alternative described.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-17 — network / null

Wi-Fi keeps dropping.

- Category: The description identifies lost or malfunctioning connectivity.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-18 — network / null

VPN authenticates, then times out.

- Category: The description identifies lost or malfunctioning connectivity.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-19 — network / null

IP addresses work, names don't.

- Category: The description identifies lost or malfunctioning connectivity.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-20 — network / null

Packets are being lost across the whole connection.

- Category: The description identifies lost or malfunctioning connectivity.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-21 — network / medium

The wired network won't connect. I'm working over Wi-Fi.

- Category: The description identifies lost or malfunctioning connectivity.
- Base priority: The description includes an available working workaround.
- reference_eligible: `false`; review: `pending`; work_blocked: `false`.

## WEAK-22 — network / high

Without internet I can't send today's settlement. I have no other connection.

- Category: The description identifies lost or malfunctioning connectivity.
- Base priority: An important task is blocked with no available alternative described.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-23 — network / critical

The whole branch has no network. Nobody can take orders, no backup connection.

- Category: The description identifies lost or malfunctioning connectivity.
- Base priority: An essential service for multiple people is blocked with no fallback.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-24 — software / null

The program closes when saving.

- Category: The description identifies a malfunctioning program feature.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-25 — software / null

CSV export throws an exception.

- Category: The description identifies a malfunctioning program feature.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-26 — software / null

The calendar doesn't refresh entries.

- Category: The description identifies a malfunctioning program feature.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-27 — software / null

The application freezes when opening a PDF.

- Category: The description identifies a malfunctioning program feature.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-28 — software / high

The signing program won't start. Contract due today, only this program is permitted.

- Category: The description identifies a malfunctioning program feature.
- Base priority: An important task is blocked with no available alternative described.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-29 — software / critical

After the update, the sales program crashes for everyone. No orders can be taken, no alternative.

- Category: The description identifies a malfunctioning program feature.
- Base priority: An essential service for multiple people is blocked with no fallback.
- reference_eligible: `false`; review: `pending`; work_blocked: `true`.

## WEAK-30 — software / null

It doesn't save the view settings.

- Category: The description identifies a malfunctioning program feature.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-31 — null / null

It doesn't work.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-32 — null / null

Same thing again.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-33 — null / null

Urgent!!!

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-34 — null / null

Everything's falling apart.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-35 — null / null

Really slow.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-36 — null / null

I can't get in.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-37 — null / null

An error since this morning.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-38 — null / null

Can't get anything done.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-39 — null / null

Still no good after restarting.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-40 — null / null

That thing keeps disappearing.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-41 — null / null

When I click, it goes wrong.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-42 — null / null

It was fine yesterday.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-43 — null / null

I have the same problem as the others.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-44 — null / null

Please take a look at this.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-45 — null / null

It keeps kicking me out.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-46 — null / null

What's needed isn't there.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-47 — null / null

It just keeps spinning.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-48 — null / null

It's red all the time.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-49 — null / null

It won't go any further.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.

## WEAK-50 — null / null

Help, I don't know what happened.

- Category: No symptoms that distinguish a category; clarification is required.
- Base priority: Insufficient information about impact and workarounds; no reference priority is assigned.
- reference_eligible: `false`; review: `pending`; work_blocked: `null`.
