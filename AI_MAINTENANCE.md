# How I use a bot to help maintain this repo

Hi, I'm Grant. If you've been scrolling through issues and pull requests here, you've probably noticed a bot doing a lot of the replying. I want to explain what it's doing, and what it isn't.

Manim started as the tool I wrote to make 3Blue1Brown videos, and that's still what it is for me. More issues and pull requests come in than I can keep up with on my own, and good contributions have sometimes waited far too long for a response. The bot is there to help with that.

## What the bot does

- Reads new issues, tries to reproduce them, and asks follow-up questions.
- Reviews pull requests and leaves a recommendation. For anything visual, it includes a before-and-after animation so the change is easy to see.
- Sometimes opens a pull request with a fix, with tests where it can. If someone has already opened a good pull request, it reviews that one rather than replacing it, and it credits the original author whenever it builds on their work.

## What stays with me

- The bot doesn't merge anything. Every merge is a decision a person makes.
- I still care a lot about knowing what's in this code. It's the thing I use every day, and I don't want parts of it that I don't understand.
- The animating is still me. Working through a scene forces me to get clear on what I'm actually trying to show, and that's one of the main ways I come to understand the math better. That's not something I'd want to hand off, and it isn't what the bot is for.

## If you're contributing

- Every pull request, review, and comment from the bot opens with a link to this page, so you can always tell when you're hearing from it rather than from me.
- If it gets something wrong, or you'd like a person to take a look, just say so in the thread.

Thanks to everyone who takes the time to report bugs and send fixes. It genuinely helps.

— Grant
