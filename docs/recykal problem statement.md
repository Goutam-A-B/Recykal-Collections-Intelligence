# Recykal Technologies — Strategy Analyst Intern Assessment
## Problem Statement

Recykal operates a large-scale B2B circular economy marketplace where recyclers purchase scrap materials across categories such as Metals, Plastics, and Paper. Every shipment dispatched to a recycler generates an invoice, and the Collections team is responsible for ensuring timely payment recovery against those invoices.

As transaction volume grows, the existing collections workflow becomes increasingly difficult to manage manually. The collections team must continuously track invoices, monitor due dates, calculate outstanding balances after partial payments, follow up with customers at the correct time, and maintain visibility into collection performance in real time. Since shipment and payment records are updated continuously, static or manually maintained workflows are not reliable or scalable.

The assignment focuses on solving this operational and financial visibility challenge by building two integrated systems:

1. An Automated Payment Reminder & Balance Confirmation System
2. A Real-Time Collections Dashboard in Google Sheets

The solution must work dynamically with live-updating transactional data and automate the most repetitive and error-prone collection activities.

---

# Business Context

Recykal maintains operational data across three interconnected datasets:

- `customers` → master data of recycler companies
- `shipments` → shipment and invoice-level transactional data
- `payments` → payment records received against shipments

These datasets are linked using `customer_id` and `shipment_id`.

The business process works as follows:

1. Scrap material is dispatched to a recycler
2. An invoice is generated for the shipment
3. The recycler is expected to pay within predefined credit terms
4. Payments may be full, partial, delayed, or missing
5. The collections team follows up until the invoice is settled

A major operational challenge arises because:
- payments can occur in multiple installments,
- overdue invoices must be tracked continuously,
- reminders must be sent at precise intervals,
- large customers require different handling logic,
- and new records are added automatically every day.

The current process likely depends heavily on manual tracking, increasing the risk of:
- delayed collections,
- missed reminders,
- incorrect outstanding calculations,
- inconsistent customer communication,
- and lack of real-time visibility into receivables.

---

# Core Problem

The core problem is the absence of an intelligent, automated, and scalable collections management workflow that can:

- continuously monitor invoice payment status,
- calculate accurate outstanding balances,
- automate customer communication,
- differentiate handling based on customer segment,
- and provide real-time decision-making visibility to the collections team.

The solution must eliminate manual dependency while ensuring business-rule accuracy.

---

# Objective of the Assignment

The assignment aims to design a system that improves collections efficiency, reduces overdue payments, and provides operational transparency through automation and live analytics.

The final system should achieve the following:

## 1. Automate Payment Reminder Workflows

The system must automatically identify invoices approaching or crossing their due dates and trigger appropriate reminder emails based on predefined business rules.

The automation must:
- reduce manual follow-up effort,
- ensure timely reminders,
- improve payment recovery rates,
- and maintain standardized communication.

---

## 2. Correctly Handle Outstanding Balance Logic

A critical objective is accurate receivable tracking.

The system must:
- detect fully unpaid invoices,
- calculate remaining balances after partial payments,
- prevent reminders for fully settled invoices,
- and ensure that communication reflects actual dues instead of original invoice values.

This is one of the most important evaluation criteria in the assignment.

---

## 3. Support Business-Specific Collection Rules

The workflow must incorporate operational business logic rather than generic automation.

Examples include:
- different reminder stages,
- excluding Large segment customers from automated overdue notices,
- including specific invoice metadata in emails,
- and running monthly balance confirmation workflows.

This ensures the solution aligns with actual enterprise collections operations.

---

## 4. Provide Real-Time Collections Visibility

The dashboard must function as a live monitoring system for the collections team.

It should provide:
- total invoice exposure,
- current collections,
- overdue monitoring,
- customer-level outstanding analysis,
- invoice aging analysis,
- and recent payment trends.

The dashboard must automatically update when new rows are added and should not rely on fixed ranges or manual refresh logic.

---

# Functional Requirements

# Task A-1 — Automated Payment Reminder System

The system must send automated reminder emails based on invoice due dates.

## Reminder Trigger Logic

| Trigger Window | Required Action |
|---|---|
| 7 days before due date | Send 7-Day Reminder |
| 3 days before due date | Send 3-Day Reminder |
| 1 day before due date | Send Final Reminder |
| After due date with outstanding balance > 0 | Send Overdue Notice |

---

## Mandatory Conditions

The system must ensure:

- Only invoices with pending outstanding amounts receive reminders
- Fully paid invoices are excluded
- Partial payments are reflected correctly
- Outstanding amount shown must be the remaining balance
- Large segment customers do not receive automated overdue notices
- Every email contains:
  - Customer Name
  - Shipment ID
  - Invoice Amount
  - Amount Paid
  - Outstanding Balance
  - Due Date
  - Days until or since due date
- Emails run automatically through scheduled triggers
- All automated emails include:
  `ai-strategy-interns-case-submissionsleads@recykal.com` in CC

---

# Task A-2 — Monthly Balance Confirmation

The system must generate one consolidated monthly email per customer containing:

- all unpaid shipments,
- partially paid shipments,
- shipment-wise outstanding balances,
- and total outstanding exposure.

This workflow should:
- run automatically on the 1st day of every month,
- support customer reconciliation,
- and allow buyers to confirm or dispute balances through email replies.

---

# Task B — Real-Time Collections Dashboard

The dashboard must provide a live operational view of receivables and collections performance.

## Required Dashboard Components

### 1. Summary KPIs
The dashboard must display:
- Total Invoice Value
- Total Collected
- Total Outstanding
- Number of Overdue Shipments

---

### 2. Outstanding by Customer
A customer-level receivables table sorted from highest to lowest outstanding balance.

Purpose:
- prioritize collection efforts,
- identify high-risk accounts,
- and monitor exposure concentration.

---

### 3. Invoice Aging Buckets
Outstanding invoices must be grouped into:
- Not Yet Due
- 1–30 Days Overdue
- 31–60 Days Overdue
- 61+ Days Overdue

Purpose:
- identify collection risk,
- monitor delayed payments,
- and improve recovery prioritization.

---

### 4. Daily Collections Trend
A trend visualization showing amount collected per day over the previous 30 days.

Purpose:
- analyze collection performance,
- identify collection slowdowns,
- and monitor cash inflow consistency.

---

# Technical Expectations

The solution is expected to be:
- dynamic,
- scalable,
- automated,
- and business-rule aware.

Key technical expectations include:
- dynamic range handling,
- no hardcoded row references,
- automated scheduled execution,
- proper table relationships,
- accurate aggregation logic,
- real-time updates,
- and reliable outstanding calculations.

The system should gracefully handle continuously arriving records without requiring manual intervention.

---

# Evaluation Focus Areas

The assignment evaluates both technical correctness and business thinking.

The solution will primarily be judged on:

## 1. Originality of Solution
Ability to leverage automation and AI meaningfully instead of creating a generic workflow.

---

## 2. Accuracy of Outstanding Calculations
The most critical functional requirement.

The system must:
- correctly aggregate payments,
- support partial payments,
- prevent false reminders,
- and calculate live balances accurately.

---

## 3. Business Rule Compliance
The solution must strictly follow:
- reminder timing rules,
- segment-based exclusions,
- overdue handling logic,
- and email content requirements.

---

## 4. Dashboard Usefulness
The dashboard should be actionable, readable, and operationally valuable for the collections team.

---

## 5. Documentation & Reasoning
The thought process behind architectural decisions, formulas, automation logic, and assumptions must be clearly explained.

---

# Expected End Result

The final solution should function as a lightweight automated collections intelligence system that:

- reduces manual collection effort,
- improves receivable tracking accuracy,
- minimizes overdue payments,
- provides real-time operational visibility,
- supports scalable collections management,
- and enables proactive financial follow-ups.

The system should be robust enough to operate continuously on live transactional data with minimal human intervention.

