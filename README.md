# Smart Poll

A [Maubot](https://github.com/maubot/maubot) plugin for
[Matrix](https://matrix.org/), which enables polls in matrix rooms.
The polls are *text-based*, so that they can also be used via bridges.

This repository originates from a forked repository
[maubot-poll](https://github.com/YingzhouLi/maubot-poll), which is a
English translated version of the original
[maubot-poll](https://github.com/DrDeee/maubot-poll) by
[@DrDeee](https://github.com/DrDeee).


## Installation

Upload the `smartpoll-v0.0.0.mbc` file via Maubot user interface.
You could generate your own mbc file via
[`mbcbuild.sh`](/mbcbuild.sh) script in the
source code. Alternatively, you could download the plugin from the
[Tags](./tags).

## Usage [To Be Updated Accordingly]

- `!poll create <question> | <option 1> | <option 2> | <...>` -  Creates a new poll
- `!vote <code> <option>` - Vote for an option
- `!poll result <code>` - Shows the result of the poll
- `!poll ping <code> <option>` - Pings all participants who voted for `option`

