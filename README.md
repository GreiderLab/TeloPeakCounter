# TeloPeakCounter

TeloPeakCounter is an algorithm that takes in a signal from a nanopore sequencing run and returns the telomere length of the sample.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

TeloPeakCounter requires the following packages to be installed:

```
statistics
numpy
matplotlib
```

## Usage

### TeloPeakCounter Function Arguments

TeloPeakCounter reads in fast5 data, which can be extracted using SquigglePull. Once extracted, the getTeloCountLengthFromSignal
function can be used to get the telomere length of the sample. The parameters for this function are as follows:

```
getTeloCountLengthFromSignal(signalIn, isGStrand, ceilingWindow = 500)

signalIn: The signal data from the fast5 file
isGStrand: True if the sample is the G strand, False if it is the C strand
ceilingWindow: The window size used to calculate the ceiling of the signal. A larger window will result in a smoother ceiling, but may not be as accurate.
```

The **Gstrand** value can be calculated using chromosome arm information from strand alignments.
The **ceiling** window value is explained in more detail bellow.

## TeloPeakCounter Algorithm Description

TeloPeakCounter works in two parts. First the algorithm finds the telomeric region of the signal, then it counts the number of peaks in that region.

### Region Identification

The telomeric region can be identified thanks to the high periodicity of the signal. The telomere region moves within a more restricted range
than the rest of the signal, so we can scan for this to find the telomere region. The algorithm first calculates a "ceiling" for the signal,
which is the highest value in a given window (the ceilingWindow) of the signal.

The following graph is an example showing the signal (blue) and the ceiling (orange) of the signal.

---

Once these ceiling values have been calculated, we make the assumption that all reads have telomere and that the telomere is at the end of the read.
We then use a "stepBack" value to find the index of telomeric signal data, and use this to identify what hight the telomeric region should be.

Now that we know the "ceiling height" of the telomeric region within the signal, we scan forward and backwards to identify the boundaries of
this region. Once this is done, we get a graph that looks like this:

---

### Peak Counting

Finally, we go onto step two, where we count the number of peaks in the telomeric region. This section is rather simple. Two thresholds are used,
one to start counting a "peak", and another to mark the end of a "peak". For example, imagine a wave signal moving upwards, starting at 0 and going
to 100. The first threshold my be at 50, so the algorithm will start counting the peak once the signal goes above 50. The second threshold may be at 80,
so the algorithm will stop counting the peak once the signal goes below 80. These values are just examples, and the actual values used were determinted
by manually inspecting the signal data and determining the best way to count the peaks.

The following graph shows a close up of the telomeric region, with the peaks marked in **\***

---

## Notes:

This algorithm was designed to help validate the telomere lengths producted by the Guppy and Dorado basecallers.
