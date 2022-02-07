# Smart Poll

A [maubot](https://github.com/maubot/maubot) plugin for
[Matrix](https://matrix.org/), which enables polls in matrix rooms.
The polls are *text-based*, so that they can also be used via bridges.

This repository originates from a forked repository
[maubot-poll](https://github.com/YingzhouLi/maubot-poll), which is a
English translated version of the original
[maubot-poll](https://github.com/DrDeee/maubot-poll) by
[@DrDeee](https://github.com/DrDeee). This bot also learns from
[Poll Maubot](https://github.com/TomCasavant/PollMaubot).


## Installation

Upload the `smartpoll-v0.0.0.mbc` file via Maubot user interface.
You could generate your own mbc file via
[`mbcbuild.sh`](/mbcbuild.sh) script in the
source code. Alternatively, you could download the plugin from the
[Tags](../../tags).

## Usage

- Create a new poll

  ```
  !poll create <question> | <option 1> | <option 2> ...
  ```
    - Alternatively, a new poll can be created as follows,
      ```
      !poll create <question>
      <option 1>
      <option 2>
      ...
      ```
- Vote for choice(s)
  
  There will be emojis :one:, :two:, :three:, etc. attached to the poll
  from the bot. Users can simply click the emoji to vote for choice(s)

- Show the result of the poll (creator only)

  ```
  !poll result <code>
  ```

- Pings all participants who voted for `choice` (creator only)
  ```
  !poll ping <code> <choice>
  ```

- Close the result of the poll (creator only)

  ```
  !poll close <code>
  ```

## TODO List

- Add `list` functionality to list active and/or closed polls
- Connect with database so that a closed poll result is still accessible
- Enable result/close/ping without `<code>` to show the output related to
    the most recent active poll.
- Add multiple-choice poll so that only a single choice counts
- Add private vote functionality so that users can vote in a private room
    with the bot and the creator can only view the poll results and cannot
    ping choice.

## Contributors
  <a href="https://github.com/YingzhouLi/smartpoll/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=YingzhouLi/smartpoll" />
  </a>

  Made with [contrib.rocks](https://contrib.rocks).
