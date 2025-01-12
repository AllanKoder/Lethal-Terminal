# Lethal Terminal

'Lethal Terminal' is an advanced terminal tool for automating disarming mines, turret, and easily performing macros with vim motions.

<p align="center">
  <img src="./assets/lethal_terminal.ico" alt="Lethal Terminal icon" />
</p>

## Features:
- Automatically typing all the mines and turrets every 5 seconds (configurable)
- Using Vim-like motions to switch between different states: ex: adding traps, removing, inputting text.
- Macros for:
    - switching player
    - pinging radar
    - flashing radar
    - transmitting messages
    - view monitor
    - purchasing a single walkie talkie

<p align="center" style="padding: 20px">
  <img src="./assets/terminal_gameplay.png" alt="Lethal Terminal icon" />
  <i>Terminal UI to display state</i>
</p>

## Guide (How to Use)

Getting used to vim controls is tricky at first, here is a chart of the states and the transition commands between them:

> Note: 'trap' means a mine, or a turret

| **State**            | **Description**                                    | **Key Commands**                      |
|----------------------|----------------------------------------------------|---------------------------------------|
| **Gameplay**         | The main game state where the user interacts.     | `t + enter` → Terminal                |
| **Terminal**         | Command input state for various actions.           | `tab + tab` → Gameplay <br> `a` → Add Trap <br> `x` → Remove Trap <br> `i` → Insert Text <br> `s` → Switch User <br> `t` → Transmit Text <br> `v` → View Monitor <br> `p` → Ping Radar <br> `f` → Flash Radar <br> `q + q` → Toggle Traps <br> `b + b` → Buy Walkie Talkie |
| **Any State Below (except Gameplay)**         |           | `control + c` → Return to **Terminal** state |
| **Add Trap**         | State for adding a new trap to the trap list.     | Backspace to delete, then enter trap (e.g., a1) |
| **Remove Trap**      | State for removing a trap from the trap list.     | Backspace to delete, then enter trap (e.g., a1) |
| **Insert Text**      | State for inserting text into the terminal.        | Any character input followed by `enter` |
| **Switch User**      | State for switching between users.                 | `s` → types 'switch' <br> `<player number from grid>` → 'switch <player name>' |
| **Transmit Text**    | State for transmitting a message.                  | Type message and press `enter`       |
| **View Monitor**     | State for viewing monitor text.                     | Triggered by pressing `v`             |
| **Ping Radar**       | State for pinging radar.                           |`<radar number from grid>` → 'ping (radar name)'             |
| **Flash Radar**      | State for flashing radar.                          |`<radar number from grid>` → 'flash (radar name)'             |
| **Toggle Traps**     | State for toggling all traps on or off.           | Triggered by pressing `q + q`         |

> Please note that once in any state (except gameplay), pressing  **control + c** will return back to **Terminal** state.

It will take some time to practice and get used to using this tool. I recommend trying it out on a notepad document before using it in game.

### Starting out tutorial

1. Run the executable
1. Keep the UI open on one half of the screen and the other hald is a text editor
1. Press `t+enter` in the text editor to begin `Terminal` state
1. Mess around with various states like `a` to add a trap
1. After adding a trap, notice that you will start to type the list of traps automatically
1. Even while traps are being automatically  

## Development

debugging
log levels