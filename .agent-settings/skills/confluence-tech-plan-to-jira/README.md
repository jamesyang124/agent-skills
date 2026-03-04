# Confluence to Jira Tickets Skill

Automatically generate Jira tickets from Confluence documentation.

## Overview

This skill allows the agent to read a Confluence page (like a PRD or Tech Spec), analyze its content to identify tasks, and create a corresponding root ticket with multiple subtasks in Jira.

## Usage

1.  Provide a Confluence page ID or title.
2.  The agent will analyze the content and propose a set of Jira tickets.
3.  Specify the target Jira project.
4.  The agent will create the tickets and link them.

## Requirements

- Atlassian MCP Server configured with Jira and Confluence access.
- Docker (if using the default MCP configuration).
