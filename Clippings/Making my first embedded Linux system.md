---
title: "Making my first embedded Linux system"
source: "https://popovicu.com/posts/making-my-first-embedded-linux-system/"
author:
  - "[[Uros Popovic]]"
published:
created: 2025-03-31
description: "End-to-end documentation of a journey from no PCB experience to fabricating my own Linux-ready system that can boot the latest mainline kernel. This article is the recommended reading for someone building their first embedded Linux board. F1C100s SoC is used for this sample board."
tags:
  - "BBB"
---
This post is the documentation of my journey to building [my first Linux system](https://popovicu.com/linux-board). I started with no PCB experience whatsoever and I am here to document the journey to my Linux-ready PCB.

The initial part of this text may seem somewhat off-topic, but I promise there is cohesion to all these sections, so please patiently read through the whole text.

Open Table of contents
- [Don’t be scared!](https://popovicu.com/posts/making-my-first-embedded-linux-system/#dont-be-scared)
- [Pre-reading](https://popovicu.com/posts/making-my-first-embedded-linux-system/#pre-reading)
- [Off-the-shelf PCBs and hiding the details](https://popovicu.com/posts/making-my-first-embedded-linux-system/#off-the-shelf-pcbs-and-hiding-the-details)
- [Very first custom PCB board (not Linux-ready)](https://popovicu.com/posts/making-my-first-embedded-linux-system/#very-first-custom-pcb-board-not-linux-ready)
	- [Booting a chip](https://popovicu.com/posts/making-my-first-embedded-linux-system/#booting-a-chip)
	- [Usage of programmers (i.e. “enter the dragon”)](https://popovicu.com/posts/making-my-first-embedded-linux-system/#usage-of-programmers-ie-enter-the-dragon)
	- [The dudes who program: `avrdude`](https://popovicu.com/posts/making-my-first-embedded-linux-system/#the-dudes-who-program-avrdude)
	- [What is a Dragon, and do I need it?](https://popovicu.com/posts/making-my-first-embedded-linux-system/#what-is-a-dragon-and-do-i-need-it)
	- [Designing a PCB for ATtiny](https://popovicu.com/posts/making-my-first-embedded-linux-system/#designing-a-pcb-for-attiny)
- [What goes into designing an embedded Linux system?](https://popovicu.com/posts/making-my-first-embedded-linux-system/#what-goes-into-designing-an-embedded-linux-system)
- [Inspirational design](https://popovicu.com/posts/making-my-first-embedded-linux-system/#inspirational-design)
- [Designing the schematic](https://popovicu.com/posts/making-my-first-embedded-linux-system/#designing-the-schematic)
	- [Power supply](https://popovicu.com/posts/making-my-first-embedded-linux-system/#power-supply)
	- [Crystal](https://popovicu.com/posts/making-my-first-embedded-linux-system/#crystal)
	- [Decoupling capacitors](https://popovicu.com/posts/making-my-first-embedded-linux-system/#decoupling-capacitors)
	- [Connectors, pins and IO](https://popovicu.com/posts/making-my-first-embedded-linux-system/#connectors-pins-and-io)
		- [“FEL mode” button](https://popovicu.com/posts/making-my-first-embedded-linux-system/#fel-mode-button)
	- [SPI flash](https://popovicu.com/posts/making-my-first-embedded-linux-system/#spi-flash)
	- [`SVREF` weirdness](https://popovicu.com/posts/making-my-first-embedded-linux-system/#svref-weirdness)
	- [Concrete components](https://popovicu.com/posts/making-my-first-embedded-linux-system/#concrete-components)
	- [Putting the schematic together](https://popovicu.com/posts/making-my-first-embedded-linux-system/#putting-the-schematic-together)
- [Routing the PCB](https://popovicu.com/posts/making-my-first-embedded-linux-system/#routing-the-pcb)
- [Creating the software image](https://popovicu.com/posts/making-my-first-embedded-linux-system/#creating-the-software-image)
- [Conclusion](https://popovicu.com/posts/making-my-first-embedded-linux-system/#conclusion)

## Don’t be scared!

While I’m not claiming that my design is something that should immediately go into production and be used to manage the treatment of hospital patients, I do think my prototype at least boots and runs Linux and if you’re reading this article, that’s probably your only goal to start with. Once you go through this initial hurdle, you’ll have a much better idea of where to go next to indeed get to that production readiness.

I’m sure as someone who is not a PCB expert I made a ton of rookie mistakes in my design for the [Linux board](https://popovicu.com/linux-board), but it got the job done — and it was easier than I thought it would be. If you know some basics of electrical engineering, and you’re disciplined and can spare a few hours a day, I think you may be a single-digit number of days away from putting together a similar prototype that can boot Linux. I hope that’s encouraging and I hope this text makes you cross that journey much faster.

## Pre-reading

If `V = IR` means nothing to you, probably you should take a step back and review the absolute basics of electric circuits. You should have some intuition around words like resistors, capacitors, and inductors before you proceed. That said, the rest of this text should be easy to follow with only the absolute basics in electronics (not that I know much more anyway).

## Off-the-shelf PCBs and hiding the details

PCBs like Raspberry Pi are nice and popular, but if we just keep using them, especially by following the manufacturers’ basic tutorials, we probably don’t get much idea about how things work; and we need that knowledge to make our PCBs. My observation is that this is in particular true with microcontrollers, so we’ll use that as an example.

First, let’s see what’s different with Linux, though. For example, if you use Raspberry Pi to boot Linux, or any other board, at some point, you will reach an area of familiar environment. No matter whether you’re on a full-blown desktop Linux or some tiny RPi image, you still see things like `/dev` and often run familiar commands like `ls` and so on. The reason for this is the stability of the API (ABI?) of the Linux system. Standardization like this doesn’t exist with the microcontrollers.

When you load a sample code into an Arduino board, you may be going through a completely different journey compared to an STM32 Nucleo board. Not only is the process of loading the code different, but the methodology for writing the code itself can vary wildly. We see different IDEs and flows to do the same thing: write some C code to flicker LEDs. Sadly, the manufacturers indeed often corner us into using their customized flows (presumably to increase the vendor lock-in; consciously or otherwise, use your judgment and skepticism).

## Very first custom PCB board (not Linux-ready)

After observing the above, I decided to make my own first PCB with some programmable digital logic on it and make it as simple as possible.

First of all, what does it even mean to program the board? We write some code, compile it, send it over somehow to a chip that is capable of running the compiled machine code, and observe the effects. I won’t focus on writing and compiling the code, but rather, on what happens afterward.

### Booting a chip

Thinking of some extremely simple microcontrollers, I asked myself — what happens when I power on a chip (no matter how I do it)? Where does it read the code from? And how does it give me a chance to give it some code in the first place?

A few years ago, I was looking for the cheapest possible MCUs and ran into the Atmel ATtiny MCUs (the brand is now Microchip, I believe). You can get these MCUs for like $1 per piece, if not less. Now the question is, once we have this chip, but just the chip and nothing else around it, how do we get started with it? Surely it must be very simple with such a tiny chip.

Conceptually, upon providing the power voltage, an ATtiny chip will inspect the state of its pins. If you satisfy certain conditions, such as setting some pins high or low, the chip will enter the programming mode. This mode then enables you to talk to the chip via some protocol, for example, SPI, and load its on-chip flash with some code. After you’re happy with the code you loaded, you can reset the chip, “unsatisfy” the programming conditions, and let the new code run.

### Usage of programmers (i.e. “enter the dragon”)

If I’m on my computer, however, I don’t have any individual pins or wires poking out of it to do the above, let alone run something like SPI protocol. I probably have a bunch of USB ports, and a lot of pre-cooked PCBs connect to our computers via USB for programming, so that may be the right approach.

However, I don’t have a board here, I just have my chip, so how do I go about programming over USB? ATtiny has SPI programming only, so something must bridge the gap between the USB and SPI.

In the ATtiny case, there’s something called **AVR Dragon** that’s the solution to this problem.

*Image from the [official AVR Dragon page](https://www.microchip.com/en-us/development-tool/atavrdragon)*

This is a device that you can connect to your computer via USB and drive through some software on your computer to do the signal orchestration that we mentioned above. Once your computer commands the AVR Dragon to program the ATtiny chip, AVR Dragon will satisfy the programming conditions and run the protocol (e.g. SPI) with the chip itself to fill out the on-chip flash of the microcontroller with the compiled code.

For the ATtiny use case, I was able to do the programming by connecting the Dragon and the MCU with a breadboard. Programming would fail until I figured out there’s a parameter to slow down the data rate of the code upload to the MCU, and once I did that, the breadboard setup worked just fine. All I had to do for the most part was hook up AVR Dragon’s SPI to my chip’s SPI.

### The dudes who program: avrdude

We now have the hardware solution to the USB -> SPI dance, but what on our host computer would make this programming happen?

There needs to be an application that would drive the messages on the USB port to the Dragon. In my case, I used `avrdude`. It’s an open-source application that can program various Atmel/Microchip chips, including the ATtiny series. One of the parameters to the `avrdude` is what kind of programming you’re doing. In my case, it was as simple as setting one of the flags to something like `avr_dragon`.

With this, I was able to load up my ATtiny with some code, then power it down, put it on another breadboard, and flicker some LEDs.

Great, so now I have a few important pieces of info if I were to do a PCB with ATtiny chips:

- I either program the chips like here, on a separate surface, and “drop” them into their operating environment, or…
- Expose SPI pins so that I can hook them up to an AVR Dragon.

The latter has a somewhat obvious consequence if those same pins connect to something like LEDs, these can flicker as the Dragon is setting the pins high and low, but that’s not of huge importance here.

### What is a Dragon, and do I need it?

Now that we unpacked the end-to-end programming flow for the ATtiny, we understand that the AVR Dragon doesn’t do anything extremely complicated — as long as we have **some** device that can send out some SPI messages to the chip, we can use that device as a programmer.

Well, interestingly, `avrdude` can be used with a different flag value for the same flag that took in `avr_dragon` as the parameter. This value is meant to be used on Raspberry Pi and utilizes RPi’s GPIO pins to do the programming. A detailed write-up is [here](https://learn.adafruit.com/program-an-avr-or-arduino-using-raspberry-pi-gpio-pins/installation).

### Designing a PCB for ATtiny

At this point, I have a simple way to program my ATtiny using a breadboard and AVR Dragon connected to my computer, though I could even eliminate the Dragon if I wanted to.

My PCB goal now is to design a PCB where I have a socket in which I can plug a pre-programmed ATtiny. Once that PCB is powered on, some LEDs would flicker.

This is an extremely simple PCB. You only need a DIP-8 socket, which replaces your breadboard’s holes, and a few PCB traces which replace the jumper wires from your breadboard prototype. My circuit will be powered by a single 5 V trace that goes into the chip, then 2 traces come out of the GPIOs to power the LEDs, and then there’s a GND trace everywhere to close the circuit. Here’s the result:

And the actual PCB:

So there are 2 parts of the design here: the schematic and the physical implementation. The schematic is your textbook-like logical model of the circuit. Once you design that, you will click a button in your tool with which you’ll get a blank PCB surface to organize your components and connect them. The schematic drives your work here and your EDA tool can use it to catch errors, e.g. if you’re trying to make connections that exist nowhere in your schematic.

You can watch a somewhat lengthy absolute beginner 7-piece tutorial by Robert Feranec on building out your first PCB, though it can get fairly long. I’d say it’s worth at least just scanning through to see a knowledgeable person in action:

![](https://www.youtube.com/watch?v=videoseries)

Now that I’ve gone through this experiment successfully, I thought let’s just go all in and make an embedded Linux board.

## What goes into designing an embedded Linux system?

There is a really good high-level article by Jay Carlson on getting started here, and you can find it on [this link](https://jaycarlson.net/embedded-linux/).

If you’re already sold on ‘why embedded Linux’, you can skip a decent chunk of the intro text there and hop into the design workflow section. We’ll deal with something much simpler than a BGA package, though, and we’ll also skip complex bits like DDR routing since all our RAM will be on-chip within the SoC we’ll explore. We also won’t be mega disciplined about the signal integrity as all our components will run reasonably fast (slow?) and will be forgiving when it comes to design decisions.

With that in mind, still read Jay’s article, and consider this article a gentler introduction to what Jay wrote about.

## Inspirational design

As I wrote in the text on [running Linux on $5 hardware](https://popovicu.com/posts/run-mainline-linux-on-5-dollar-hardware), my inspiration for the first embedded Linux system was [the business card that runs Linux](https://www.thirtythreeforty.net/posts/2019/12/my-business-card-runs-linux/). The fact that it’s a business card signaled to me it would be as simple as possible in its design and it would be the right design to study.

The article’s author generously posted [the schematic](https://www.thirtythreeforty.net/posts/2019/12/my-business-card-runs-linux/businesscard.pdf) for the circuit design and understanding this was the first part of the journey.

## Designing the schematic

There aren’t that many components in the inspirational design, and that seems right. After all, we have demonstrated it’s possible to boot and run Linux with just on-board flash plus an Allwinner SoC! Let’s break down the problem of designing the schematic and center it around the F1C100s SoC.

### Power supply

As Jay Carlson mentioned and the inspirational design confirms, a Linux-ready SoC will need a couple of different voltages for the power supply. If we look at the F1C100s datasheet, we see the following:

We see a couple of different voltages in the game, like `VCC-IO`, `VDD-CORE`, etc.

3.3 V seems to be the recommended voltage for a few values, so we can mark it right now that we’ll need that voltage on our board. We also see 2.5 V for `VCC-DRAM` and it’s also still within the OK values for `AVCC`. Let’s thus add 2.5 V to the list of voltages we need on-board. Finally, `VDD-CORE` has a pretty “tight” range, and we’ll add 1.1 V to our list.

The Linux board can be powered from the USB host, meaning our board will connect over USB to another machine and source 5 V from there. If this seems a bit unfamiliar, please check out my recent text on [building USB devices](https://popovicu.com/posts/making-usb-devices). That’s the only voltage we’ll have from “the external world” and we’ll need to equip our PCB with some components that can convert 5 V down to these values listed above.

We’ll use voltage regulators for these, and we need 3 of them, one for each voltage needed. We’ll put some capacitors around these voltage regulators and the way you go about finding out what you should do there is you would open the datasheet for your voltage regulator and find a section that’s titled something like “typical application”.

### Crystal

F1C100s needs some oscillation to be able to run at 24 MHz clock speed. Therefore, we need a 24 MHz crystal for that, and we’ll need some capacitors around it. Luckily, this is a well-known recipe. Please check out [this page](https://microchip.my.site.com/s/article/Calculating-crystal-load-capacitor) for this recipe (crystal + 2 capacitors).

And yes, in my design, I also estimated `Cstray` at 5 pF.

### Decoupling capacitors

We’ll need to put a bunch of decoupling capacitors around the voltage supply pins. Without talking too much outside the area of my expertise, I’ll just link to a few YouTube videos I found helpful on this topic.

The first one will give you a very high-level idea of what these capacitors do:

![](https://www.youtube.com/watch?v=KKjHZpNMeik)

The next one is an awesome video on practical use cases from Zach Peterson:

![](https://www.youtube.com/watch?v=MMY69_1U4w4)

Finally, I also found this video from EEVblog useful to expand my intuition around this capacitor usage:

![](https://www.youtube.com/watch?v=BcJ6UdDx1vg)

I pretty much used a bunch of 100 nF decoupling capacitors all over the place.

### Connectors, pins and IO

I powered the PCB via a USB connection (USB-micro connector on-board) and also used that same connection to fill up the onboard flash/RAM (more about it later). I’d say for this exercise, you’d want that the minimum.

Other pins and connections you would add at this point are your choice. How do you want your PCB to interact with the outside world? Maybe you want to expose an I2C port, a UART port, or something else, it’s really up to you.

One thing you may want to make your debugging easier is adding some LEDs, which should be easy.

#### “FEL mode” button

Going back to the article on [running Linux on $5 hardware](https://popovicu.com/posts/run-mainline-linux-on-5-dollar-hardware): FEL mode with F1C100s is very important to us. I’ll go through this again briefly in this article, but for now — I added a button that will ground the clock on the SPI flash which effectively takes it down. It may seem strange, but it makes life easier.

### SPI flash

Something went wrong here.:) I wanted a 16 MB flash chip but ended up getting 2 MB only. Not sure if I messed up or the fabricator (with its documentation or otherwise), but it doesn’t matter, I managed to bail out here. The initial ramble about programming ATtiny is an important lesson here!

More importantly, for now, there were a couple of things about the SPI flash:

- We want it to be big enough to store our Linux image and maybe even store some runtime data (optional).
- Ideally, we want it to be powered by a voltage that we already have on-board. 3.3 V should be doable.

### SVREF weirdness

There was one very weird pin on the SoC called `SVREF`. The datasheet says nothing about this pin except that it exists. In this case, I just looked at what the other designs do here and copied the approach. For this particular thing, I just applied a simple resistor-based voltage divider (take a look at the schematic from the inspirational design, for example).

### Concrete components

What we listed above is pretty much everything you need, high-level, to stitch together your Linux system. You do need, however, to figure out which components **exactly** you want to use in your design. For example, you want to use 100 nF decoupling capacitors, but there are tons of models out there that your fabricator can use, each with different characteristics (price included as a characteristic). Additionally, some of these components may be preferred by your fabricator, some of them may be added faster to your PCB, some of them may or may not be in stock, etc. In my case, I used JLCPCB and they call these “easier-to-use” parts *basic parts*.

For the prototype, make sure the parts click together well. For example, if you use a resistor, make sure it can handle the current you’d be passing through it. Additionally, pay attention to the geometry as well, aka the footprints. The footprint is the space and connection layout for your component. You’ll see different designations for things like resistors. There are 0603 resistors, but they’re bigger than 0402 resistors. I used 0402 footprints for the most part, for both capacitors and resistors.

Lastly, there’s a strong reason why I liked using EasyEDA for this exercise: they provide a massive library of components they can throw onto the PCB, along with the footprints. Very often PCB designers (as I understand, I’m not a PCB designer) spend time struggling with component datasheets and whatnot to establish what the exact footprints are and how to match them to the components they want to use — EasyEDA links very nicely with the JLCPCB fabrication process.

### Putting the schematic together

Take a look at the schematic [here](https://popovicu.com/assets/linux_board_schematic.pdf).

**Caution: Please don’t expect a very readable schematic.:) Experienced PCB people will likely recoil after seeing it. It’s just a proof-of-concept and it’s hacky. On top of that, I’m most definitely not a PCB expert. I never really meant to share this schematic, but I guess it could still be useful to some of you.**

I’ll summarize below what is going on in this schematic:

- Most of the SoC pins are unconnected. The SoC itself is `U1`.
- `U2`, `U3`, and `U4` are the voltage regulators to obtain those different voltages you need to power up the SoC.
- `U5` is the SPI NOR flash memory. Again, check out the old article on $5 hardware Linux to figure out how to boot from here and so on. This memory can be “disabled” by holding the button `U6` in the schematic, which grounds the clock signal. This enables you to restart the SoC and make it believe there is nothing to boot from, thus forcing it to enter the FEL mode.
- `U7` is the reset switch.
- `U8` and `U9` are LED drivers. Total overkill, you can just hook up your LEDs to the GPIOs.
- The decoupling capacitors should be fairly easy to spot at this point (there are a lot of them).
- `USB1` is the USB-micro connector, which both provides the raw 5 V to the voltage regulators and also gives you the differential pair you can route to the SoC for the USB communication. Check out the article [on making USB devices](https://popovicu.com/posts/making-usb-devices) to understand what’s going on here.
- `X` is the crystal and it follows the standard recipe for hooking up the crystal to the chip.
- `L1` is the ferrite bead. As I understand, many times when you plug your USB into something like an outlet with a USB port, that 5 V can be noisy, and the ferrite bead helps.
- The rest is mostly just header pins to expose signals to the outer world.

And that’s pretty much it!

## Routing the PCB

Now that we have the schematic, it’s time to route things around and end up with a real piece of electronics.

For me, a big challenge here was laying out these decoupling capacitors. They should be as close as possible to the SoC pins, per best practices (check out the videos from the above), but the SoC packaging makes things challenging here. I thought it was my lack of experience that kicked in here, but then I found a video from Phil’s Lab that goes into detail on this matter. Namely, this packaging is called a QFN package, and the pins here are quite dense, everything is pretty tiny. Even though those capacitors aren’t very big, they still cluster pretty fast around those SoC pins and things become difficult. This is when I decided to use a 4-layer PCB instead, per best practices shared by Phil. The video is below:

![](https://www.youtube.com/watch?v=PsyK1BXdclQ)

The other part that may seem challenging here is the USB routing. However, we’re only going for USB 2.0 full-speed, which is very very forgiving. Again, refresh your knowledge of USB devices [here](https://popovicu.com/posts/making-usb-devices), and don’t worry too much here. I just used EasyEDA’s differential pair routing from the USB-micro connector to the SoC. No need to pay too much attention to the trace width, and length, as long as it’s all reasonable (e.g. keep your trace length below 2 inches, I guess, and don’t use some weird width); things will just work.

Everything else should be pretty much straightforward. I used the following layer stack up: signal-GND-power-signal.

1. The top signal layer has a lot of GPIO traces, as well as the USB differential pair (from what I understand you shouldn’t hop through different layers when routing a differential pair).
2. GND is just ground, the whole layer.
3. In the power layer, I routed different voltages for powering the SoC with fairly thick traces.
4. The bottom signal layer is mostly decoupling capacitors.

I don’t think I should go into more detail on routing — I would probably give bad knowledge, so I’ll just stop here.

## Creating the software image

Ideally, I should have created a custom device tree for this board, but I was lazy and wanted to see the results right away. For my [running Linux on $5 hardware](https://popovicu.com/posts/run-mainline-linux-on-5-dollar-hardware) exercise, I created an image for Lichee Pi, which also doesn’t have much more than just SoC + flash, and I decided to use the same, it should just work.

And it did work, but there was a catch — as I said, I somehow ended up with a 2 MB on-board flash instead of 16 MB as I originally intended. It would have been lots of work to slim down the image, and I just wanted to see something work.

This is where the FEL mode shines and why it’s important to have something like that hacky button that disables on-board flash easily. I used the `sunxi-fel` tool to communicate with my SoC since it was directly exposed to my computer via the USB differential pair. One of the things that this tool can do for you is populate the RAM with some content and then boot up while preserving those contents. This is why I had that intro talk about programming ATtinys and figuring out what are the ways you can pipe the bytes into your chip and get it to run some code you want it to run.

Therefore, instead of loading the U-boot FIT image from the on-board flash, I downloaded it from my computer and booted from that point. Linux worked just fine.

To have more confidence my connection with the on-board flash works as intended, I could package the U-boot image and write it into the NOR flash storage, but putting Linux alongside that was tight. U-boot worked just fine, though.

## Conclusion

This was an extremely hacky journey, but it satisfied a lot of my curiosity, and seeing the PCB come to life after all the studying and designing and waiting for the fabrication was a great feeling. I hope you feel the same joy once you put together your first embedded Linux system too. Good luck!

Please consider following on [Twitter/X](https://twitter.com/popovicu94) and [LinkedIn](https://www.linkedin.com/in/upopovic/) to stay updated.