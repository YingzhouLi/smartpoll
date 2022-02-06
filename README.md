# Smart Poll

A [maubot](https://github.com/maubot/maubot) plugin for
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
[Tags](../../tags).

## Usage [To Be Updated Accordingly]

- Create a new poll

  ```
  !poll create <question> | <option 1> | <option 2> ...
  ```
    - Alternatively, 
      ```
      !poll create <question>
      <option 1>
      <option 2>
      ...`
      ```
      also creates a new poll.
- Vote for choice(s)
  
  There will be emojis :one:, :two:, :three:, etc. attached to the poll
  from the bot. Users can simply click the emoji to vote for choice(s)

- Show the result of the poll

  ```
  !poll result <code>
  ```
  Only poll creator can show the result.

- Pings all participants who voted for `choice`
  ```
  !poll ping <code> <choice>
  ```
  Only poll creator can ping the result of the poll.

- Close the result of the poll

  ```
  !poll close <code>
  ```
  Only poll creator can close the poll.
