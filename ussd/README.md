# Institutional Voting System

This is a secure institutional voting system that supports both web and USSD interfaces.

## Features

- User authentication with student IDs and temporary PINs
- Voting via web and USSD platforms
- Vote counting and result display
- Admin panel for managing elections and generating reports
- Security measures to prevent multiple voting and ensure data integrity

## Setup

1. Create the database using the provided SQL script.
2. Configure the database connection in src/db.php.
3. Set up Composer for autoloading by running composer dump-autoload.
4. Deploy the application to a web server.
5. Set up the USSD endpoint with Africa's Talking API.

## Usage

- Navigate to the home page to login and vote.
- Use the admin panel to manage elections and view results.
