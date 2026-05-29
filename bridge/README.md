# Sovereign Bridge

Shared async communication channel between Claude Code (Dispatch) and Cowork.

## How it works

Both Claude Code and Cowork can read/write files in `~/.sovereign/bridge/`. Messages are JSON files with a simple convention.

## Directory structure

```
~/.sovereign/bridge/
  dispatch/     <- Claude Code (Dispatch) writes here
  cowork/       <- Cowork writes here
  README.md     <- this file
```

## Message format

Each message is a JSON file named `{timestamp}_{topic}.json`:

```json
{
  "from": "dispatch" | "cowork",
  "to": "cowork" | "dispatch",
  "timestamp": "2026-03-30T12:30:00",
  "topic": "short-label",
  "body": "the actual message",
  "context": {},
  "status": "new" | "read" | "replied"
}
```

## Usage

### From your phone (telling Dispatch):
- "Write a message to Cowork about X" -> Dispatch writes to bridge/dispatch/
- "Check for messages from Cowork" -> Dispatch reads bridge/cowork/

### From Cowork desktop:
- "Check the bridge for messages" -> reads ~/.sovereign/bridge/dispatch/
- "Reply to Dispatch about X" -> writes to ~/.sovereign/bridge/cowork/

### Quick commands:
- Tell Dispatch: "bridge: [your message to cowork]"
- Tell Cowork: "check bridge" or "bridge: [your message to dispatch]"
