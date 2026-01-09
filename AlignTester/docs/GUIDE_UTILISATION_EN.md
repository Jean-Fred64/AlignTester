# User Guide - AlignTester

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Initial Configuration](#initial-configuration)
3. [Automatic Mode](#automatic-mode)
4. [Manual Mode](#manual-mode)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)
7. [Appendices](#appendices)

---

## Introduction

### What is AlignTester?

AlignTester is a modern web application for testing and adjusting floppy drive head alignment using the Greaseweazle card. The application offers two alignment modes:

- **Automatic mode** : Automated alignment that tests multiple consecutive tracks
- **Manual mode** : Interactive alignment with track navigation and real-time analysis

### Prerequisites

- **Greaseweazle** : Greaseweazle card connected via USB
- **Floppy drive** : Compatible drive connected to Greaseweazle
- **Test disk** : Formatted floppy disk (recommended for best results)
- **Web browser** : Modern browser (Chrome, Firefox, Edge, Safari)
- **Greaseweazle v1.23b** : Required for alignment modes (Windows only currently)

### Compatibility

| Platform | Interface | Automatic Mode | Manual Mode |
|----------|-----------|----------------|-------------|
| **Windows** | ✅ Functional | ✅ Available (v1.23b) | ✅ Available (v1.23b) |
| **Linux** | ✅ Functional | ❌ Not available | ❌ Not available |
| **macOS** | ✅ Functional | ❌ Not available | ❌ Not available |

**Important note** : Both alignment modes require Greaseweazle v1.23b which includes the `align` command (PR #592). This version is currently available only on Windows.

---

## Initial Configuration

### 1. Greaseweazle Detection

#### For Beginners

1. **Connect your Greaseweazle card** to your computer via USB
2. **Open AlignTester** in your browser
3. **Click "🔍 Detect Greaseweazle"** in the "Greaseweazle Information" section
4. Wait a few seconds during detection
5. If Greaseweazle is detected, you will see a green indicator with the COM port used

**💡 Tip** : The system remembers the last port used to speed up detection on subsequent uses.

#### For Experts

Automatic detection:
- Scans up to 192 serial ports (COM1-COM192 on Windows)
- Identifies Greaseweazle via USB VID/PID (VID: 1209, PID: 0001)
- Tests the saved port first to speed up detection
- Uses `gw info` to validate the connection
- Adaptive timeout: 5s for WSL, 2s for other platforms

**Manual detection** : If automatic detection fails, you can view the list of detected ports by clicking "Detected Ports" in the detection results.

### 2. gw.exe Path Configuration

#### For Beginners

1. **Expand the "Greaseweazle Information" section** by clicking the arrow
2. In "gw.exe Path Configuration", you have three options:
   - **Detect automatically** : Click "🔍 Detect automatically"
   - **Browse** : Click "Browse..." and select the `gw.exe` file
   - **Enter manually** : Type the full path in the text field

3. **Click "Set Path"** to save

**💡 Tip** : You can enter either the path to the `gw.exe` file, or the path to the folder containing `gw.exe`. The system will automatically search for the file in the folder.

#### For Experts

**Path format** :
- **Windows** : `C:\path\to\gw.exe` or `C:\path\to\folder`
- **Linux/WSL** : `/path/to/gw` or `/path/to/folder`
- **macOS** : `/path/to/gw` or `/path/to/folder`

**Automatic detection** : The system searches for `gw.exe` in:
- Current directory
- System PATH
- Common locations (Program Files, etc.)

**Validation** : The system validates that:
- The file exists
- The file is executable (`gw.exe` on Windows, `gw` on Linux/macOS)
- The file can be executed (permissions)

### 3. Drive Selection

#### For Beginners

1. **Expand the "Greaseweazle Information" section**
2. In "Drive Selection", choose the drive type:
   - **PC** : For IBM/PC drives (Drive A or B)
   - **Shugart** : For Shugart drives (DS0, DS1, DS2, DS3)

3. **Select the specific drive** :
   - PC: Drive A or Drive B
   - Shugart: DS0, DS1, DS2 or DS3

**💡 Tip** : If you don't know which drive type you have, check the "Drive Information" section by clicking "Show details".

#### For Experts

**Drive types** :

**IBM/PC (A, B)** :
- Two drives can be connected
- Each drive has an independent motor-enable line
- All PC drives are strapped for DS1 (pin 12)
- **Drive A** : Connected via a cable with twist on pins 10-16
- **Drive B** : Connected via a straight ribbon cable

**Shugart (0, 1, 2, 3)** :
- Up to 4 drives can be connected
- Drive-select lines DS0-DS3 on pins 10, 12, 14, and 16 respectively
- All drives share a common motor-select signal on pin 16

**Track 0 Troubleshooting** :
- If "Track 0 not found" error with Shugart drive strapped for DS0: Use `--drive 0` with straight cable
- If "Track 0 not found" error with PC drive and straight cable: Use `--drive B`

### 4. Drive Test

#### For Beginners

1. **Make sure Greaseweazle is connected** (green indicator visible)
2. **Click "Test Drive"**
3. You should hear the drive move (seek command to track 20)

**💡 Tip** : This test allows you to verify that the drive responds correctly to commands before starting an alignment.

#### For Experts

The drive test sends a sequence of `gw seek` commands:
- Seek to track 20
- Audio feedback for confirmation
- Uses the selected drive from settings

**Usage** : Useful for diagnosing connection or drive configuration issues.

### 5. Track 0 Verification

#### For Beginners

1. **Make sure Greaseweazle is connected**
2. **Insert a floppy disk into the drive** : A floppy disk must be present in the floppy drive to perform the verification. If possible, use a factory-formatted floppy disk for best results.
3. **Select the corresponding disk format** : It is imperative to choose the correct disk format (see "Disk Format Selection" section) for the test to be correctly validated. The format must match the inserted floppy disk.
4. **Click "Verify Track 0"**
5. Wait for verification to complete (a few seconds)
6. Check the results:
   - **✅ Track 0 Sensor OK** : Everything works correctly
   - **⚠️ Track 0 Warning** : Minor issues detected

**💡 Tip** : It is recommended to verify Track 0 before starting an alignment, especially if you encounter problems. Make sure the floppy disk is correctly inserted and that the selected format matches your floppy disk.

#### For Experts

**Important prerequisites** :
- **Floppy disk required** : A floppy disk must be inserted in the drive to perform read tests. A factory-formatted floppy disk is recommended to ensure reliable results.
- **Disk format** : The selected format is used to validate track limits and analyze results. An incorrect format can give invalid or misleading results.

Track 0 verification performs several tests (according to Section 9.9 of Panasonic manual):

**Seek Tests** :
- Seek from different tracks to Track 0
- Verifies that the Track 0 sensor responds correctly
- Tests positioning accuracy

**Read Tests** :
- Performs multiple reads on Track 0
- Uses the selected format to validate results
- Calculates average alignment percentage
- Analyzes percentage variance

**Result interpretation** :
- **Sensor OK** : All tests passed, sensor functional
- **Warnings** : Some tests failed, but sensor may still work
- **Suggestions** : Recommendations to fix detected issues

**Technical note** : Read tests require a formatted floppy disk to correctly analyze sectors and calculate alignment percentages. An incorrect format can skew results.

### 6. Disk Format Selection

#### For Beginners

1. **Select the format** from the "Disk Format" dropdown menu
2. Formats are organized by type:
   - **IBM** : ibm.1440 (1.44 MB), ibm.1200 (1.2 MB), ibm.720 (720 KB), ibm.360 (360 KB)
   - **Amiga** : amiga.amigados
   - **Apple** : apple2.gcr
   - **Commodore** : c64.gcr
   - And many more...

3. **Check the format details** displayed under the selector:
   - Number of tracks
   - Number of heads
   - Sectors per track
   - Capacity

**💡 Tip** : The selected format is shared between automatic mode and manual mode. You can change it at any time.

#### For Experts

**Supported formats** :
- IBM formats (MFM/FM): ibm.1440, ibm.1200, ibm.720, ibm.360, etc.
- Amiga formats: amiga.amigados, amiga.adf, etc.
- Apple formats: apple2.gcr, mac.gcr, etc.
- Commodore formats: c64.gcr, etc.
- HP formats: hp.mmfm
- DEC formats: dec.rx02
- And many other formats defined in `diskdefs.cfg`

**Limit validation** :
- The system validates that tested tracks are within format limits
- Displays warnings for out-of-limit tracks
- Automatically excludes out-of-limit tracks from final calculation

**Formatting detection** :
- Analyzes if the track is formatted, partially formatted, or unformatted
- Calculates a confidence score based on:
  - Detected sector ratio
  - Number of flux transitions
  - Data density

---

## Automatic Mode

### Overview

Automatic mode performs an automated alignment by testing multiple consecutive tracks. This is the recommended mode for a complete and standardized alignment.

### Starting an Automatic Alignment

#### For Beginners

1. **Select the disk format** (see Configuration section)
2. **Configure the parameters** :
   - **Number of cylinders** : Number of tracks to test (default: 80)
   - **Number of retries** : Number of reads per track (default: 3)

3. **Click "Start alignment"**
4. **Monitor the progress** :
   - Progress bar
   - Number of values collected
   - Current cylinder

5. **Wait for completion** or click "Cancel" to stop

**💡 Tip** : Use the **Space** key to quickly start/stop the alignment.

#### For Experts

**Detailed parameters** :

**Number of cylinders (1-160)** :
- Corresponds to the number of tracks to test
- Each track has two sides (head 0 and head 1)
- Limit of 160 values used for final calculation (80 tracks × 2 sides)
- Recommended value: 80 (for a standard 1.44 MB floppy)

**Number of retries (1-10)** :
- Number of reads performed per track
- More retries = more precision but more time
- Recommended value: 3 (good compromise)

**Disk format** :
- Used to validate track limits
- Influences formatting detection
- Can be changed during alignment (will be applied to next tracks)

**Command executed** :
```bash
gw align --device <port> --drive <drive> --format <format> --cylinders <cylinders> --retries <retries>
```

### Real-Time Monitoring

#### For Beginners

During alignment, you will see:
- **Progress bar** : Completion percentage
- **Values collected** : Number of tracks tested
- **Current cylinder** : Track currently being tested

**💡 Tip** : Results are updated in real-time via WebSocket. You can see values accumulate as they come in.

#### For Experts

**WebSocket communication** :
- `alignment_update` messages: New alignment value detected
- `alignment_complete` messages: Alignment completed with final statistics
- `alignment_cancelled` messages: Alignment cancelled by user
- `alignment_error` messages: Error during alignment

**Real-time parsing** :
- Extraction of `[XX.XXX%]` values from `gw align` output
- Parsing of track numbers (format `XX.Y`)
- Calculation of intermediate statistics
- Format limit validation

### Automatic Alignment Results

#### For Beginners

After alignment completion, you will see:

**Main statistics** :
- **Average** : Average alignment percentage (target: ≥99%)
- **Minimum** : Lowest value detected
- **Maximum** : Highest value detected
- **Quality** : Classification (Perfect, Good, Average, Poor)

**Interpretation** :
- **Perfect (≥99%)** : Excellent alignment, drive is perfectly calibrated
- **Good (97-98.9%)** : Good alignment, acceptable for most uses
- **Average (96-96.9%)** : Average alignment, may require adjustment
- **Poor (<96%)** : Poor alignment, adjustment necessary

**💡 Tip** : Check the detailed table to see results by track and identify problematic tracks.

#### For Experts

**Calculated statistics** :

**Base values** :
- `total_values` : Total number of values found
- `used_values` : Number of values used for calculation (limit: 160)
- `track_max` : Last track read (format `XX.Y`)
- `track_normal` : Number of tracks used (generally `used_values / 2`)

**Advanced analysis per track** :
- **Alignment percentage** : Based on detected sectors
- **Consistency** : Standard deviation between reads (target: ≥90%)
- **Stability** : Timing variation (target: ≥90%)
- **Positioning** : Status (correct/unstable/poor)
- **Azimuth** : Score and status (excellent/good/acceptable/poor)
- **Asymmetry** : Score and status (excellent/good/acceptable/poor)

**Multi-criteria calculation** :
- **Weights** : 40% sectors, 30% quality, 15% azimuth, 15% asymmetry
- **Confidence factors** : Adjustment based on data availability
- **Penalties** : Application of penalties for out-of-limit values

**Charts** :
- **Percentage evolution** : Line chart showing evolution by track
- **Quality distribution** : Bar chart showing distribution

### Cancelling an Alignment

#### For Beginners

1. **Click "Cancel"** during alignment
2. Data collected so far is preserved
3. You can view partial results

**💡 Tip** : You can also use the **Space** key to quickly cancel.

#### For Experts

Cancellation:
- Sends an interrupt signal to the `gw align` process
- Preserves data collected up to cancellation
- Updates status to `cancelled`
- Allows viewing partial statistics

---

## Manual Mode

### Overview

Manual mode allows interactive alignment with track navigation and real-time analysis. This is the recommended mode for precise and targeted adjustment.

### Starting Manual Mode

#### For Beginners

1. **Switch to the "Manual Mode" tab**
2. **Select the disk format** (if necessary)
3. **Choose the alignment mode** :
   - **Direct Mode** : Quick adjustment (~150-200ms per read)
   - **Fine Tune** : Precise adjustments (~500-700ms per read)
   - **High Precision** : Final validation (~2-3s per track)

4. **Click "Start Manual Mode"**
5. The mode starts and begins continuous reads automatically

**💡 Tip** : Use the **Space** key to quickly start/stop manual mode.

#### For Experts

**Alignment modes** :

**Direct Mode** :
- **Reads** : 1
- **Delay** : 0ms
- **Timeout** : 5s
- **Estimated latency** : ~150-200ms
- **Usage** : Real-time quick adjustment of alignment screws
- **Optimization** : Single WebSocket message per read (saturation issue resolved)

**Fine Tune** :
- **Reads** : 3
- **Delay** : 100ms between reads
- **Timeout** : 10s
- **Estimated latency** : ~500-700ms
- **Usage** : Precise adjustments with average of multiple reads

**High Precision** :
- **Reads** : 5
- **Delay** : 200ms between reads
- **Timeout** : 15s
- **Estimated latency** : ~2-3s per track
- **Usage** : Final validation with in-depth analysis

**Command executed** :
```bash
gw align --device <port> --drive <drive> --format <format> --track <track> --head <head> --reads <reads> --delay <delay>
```

### Track Navigation

#### For Beginners

**Navigation buttons** :
- **← -5** : Move back 5 tracks
- **← -1** : Move back one track
- **+1 →** : Move forward one track
- **+5 →** : Move forward 5 tracks

**Quick jump** :
- **Buttons 10, 20, 30... 80** : Go directly to the corresponding track

**Special controls** :
- **Head 0/1 (H)** : Change head (side 0 or side 1)
- **Recalibrate (R)** : Return to track 0

**💡 Tip** : Use keyboard shortcuts to navigate faster:
- **+/-** : Move forward/back one track
- **1-8** : Go to track 10, 20, 30... 80
- **H** : Change head
- **R** : Recalibrate

#### For Experts

**Navigation without mode started** :
- Navigation works even if manual mode is not started
- Uses `gw seek` command directly
- Position is saved in localStorage
- Allows positioning the head before starting the mode

**Navigation with mode started** :
- Uses `gw align` command with incremental navigation
- Maintains continuous read stream
- Updates position in real-time
- Synchronizes with backend via WebSocket

**Commands used** :
- `gw seek --device <port> --drive <drive> --track <track> --head <head>` : Direct navigation
- `gw align --device <port> --drive <drive> --format <format> --track <track> --head <head>` : Navigation with alignment

### Manual Analysis

#### For Beginners

1. **Navigate to the track to analyze** (see Navigation section)
2. **Click "Analyze with selected format (A)"**
3. **Wait for analysis to complete** (a few seconds)
4. **Check the results** :
   - Alignment percentage
   - Number of sectors detected
   - Quality (Perfect, Good, Average, Poor)
   - Calculation details (if available)

**💡 Tip** : Analysis works even if manual mode is not started. It analyzes the current track (or track 0.0 by default).

#### For Experts

**Analysis operation** :
- Reads the current track multiple times (according to alignment mode)
- Uses selected format to validate limits
- Calculates alignment percentage based on detected sectors
- Analyzes track formatting
- Calculates consistency and stability
- Calculates azimuth and asymmetry (if available)

**Command executed** :
```bash
gw align --device <port> --drive <drive> --format <format> --track <track> --head <head> --reads <reads> --delay <delay>
```

**Detailed results** :
- **Raw scores** : Sectors, quality, azimuth, asymmetry
- **Penalized scores** : Adjusted according to limits
- **Weights used** : Criteria distribution (40% sectors, 30% quality, 15% azimuth, 15% asymmetry)
- **Confidence factors** : Adjustment based on data availability

### Continuous Reads

#### For Beginners

When manual mode is started, reads are done automatically in continuous mode:
- **Direct Mode** : One read every ~150-200ms
- **Fine Tune** : Three reads every ~500-700ms
- **High Precision** : Five reads every ~2-3s

**Real-time display** :
- **Last read** : Percentage, sectors, quality
- **History** : Last 5-10 reads (depending on mode)
- **Timings** : Duration and latency (Fine Tune and High Precision modes only)

**💡 Tip** : Use continuous reads to adjust alignment screws in real-time. Monitor the displayed percentage and adjust until you get ≥99%.

#### For Experts

**WebSocket data stream** :

**Direct Mode** :
- `direct_reading_complete` message: Single notification per read
- Optimized to avoid saturation (issue resolved)
- Minimal latency: ~150-200ms

**Fine Tune and High Precision modes** :
- `reading` messages: Notification for each read in progress
- `reading_complete` messages: Notification when a read series is complete
- Complete history with detailed timings

**Collected data** :
- **Flux transitions** : Number of magnetic transitions detected
- **Time/revolution** : Time for a complete revolution
- **Latency** : Time between two consecutive reads
- **Duration** : Total read time

**Timing analysis** :
- **Average duration** : Average time per read
- **Average latency** : Average time between reads
- **Variance** : Mechanical stability indicator

### Results Display

#### For Beginners

**Current position** :
- **Track** : Current track number
- **Head** : Current head (0 or 1)
- **Position** : Format `T<track>.<head>`

**Last analysis** :
- **Percentage** : Alignment percentage (target: ≥99%)
- **Quality** : Classification (Perfect, Good, Average, Poor)
- **Sectors** : Number of sectors detected / expected

**Read history** (if mode started):
- List of last reads with percentage and sectors
- Timings (Fine Tune and High Precision modes only)

**💡 Tip** : Results are updated in real-time. Monitor the percentage to see the effect of your adjustments.

#### For Experts

**Direct Mode display** :
- **Last read** : Percentage, sectors, visual indicator
- **Calculation details** : Raw scores, penalized scores, weights, confidence factors
- **Optimization** : Simplified display for minimal latency

**Fine Tune and High Precision modes display** :
- **Last read** : Percentage, sectors, detailed timings
- **History** : Last 10 reads with latency
- **Statistics** : Average duration, average latency, number of reads
- **Calculation details** : Complete scores with azimuth and asymmetry

**Visual indicators** :
- **Progress bars** : Visual representation of percentage
- **Symbols** : ✓ (excellent), ○ (good), ⚠ (average), ✗ (poor)
- **Colors** : Green (≥99%), Blue (≥97%), Yellow (≥96%), Red (<96%)

### Stopping Manual Mode

#### For Beginners

1. **Click "Stop Manual Mode"**
2. Continuous reads stop
3. Information from the last analysis remains displayed

**💡 Tip** : You can restart manual mode at any time. The current position is preserved.

#### For Experts

Stopping:
- Sends a stop signal to the backend
- Stops continuous read stream
- Preserves collected data
- Updates status to `stopped`
- Allows restarting without losing position

---

## Advanced Features

### Data Reset

#### For Beginners

1. **Click "Reset Data"** at the top right
2. Statistics and charts are reset
3. Selected format is preserved

**💡 Tip** : Use this function to clear results from a previous alignment before starting a new one.

#### For Experts

**Reset Data** :
- Resets displayed alignment data
- Preserves selected format
- Preserves settings (drive, gw.exe path)
- Sends WebSocket `alignment_reset` message to synchronize all clients

**Usage** : Useful for cleaning the interface before a new alignment or for comparing multiple alignments.

### Hard Reset

#### For Beginners

1. **Click "HARD RESET"** at the top right
2. **Confirm** in the dialog box
3. Greaseweazle hardware is reset

**⚠️ Warning** : This operation completely resets the hardware. Use it only in case of problems.

#### For Experts

**Hard Reset** :
- Sends `gw reset` command to hardware
- Completely resets the Greaseweazle device
- May resolve communication or state issues
- Requires confirmation to avoid errors

**Command executed** :
```bash
gw reset --device <port>
```

**Usage** : In case of:
- Persistent communication errors
- Inconsistent device state
- Detection problems

### Keyboard Shortcuts

#### For Beginners

**Automatic Mode** :
- **Space** : Start/Stop alignment

**Manual Mode** :
- **Space** : Start/Stop manual mode
- **+/-** : Move forward/back one track
- **1-8** : Go to track 10, 20, 30... 80
- **H** : Change head
- **R** : Recalibrate (return to track 0)
- **A** : Analyze current track

**💡 Tip** : Shortcuts work only when focus is not in an input field.

#### For Experts

**Event handling** :
- Shortcuts are handled via `addEventListener('keydown')`
- Ignores keys if focus is in an input/select/textarea
- Uses `preventDefault()` to avoid default behaviors
- Stores handlers in refs to avoid dependency issues

**Optimization** :
- Single listener per component
- Automatic cleanup on unmount
- Async handling for API calls

### Language Change

#### For Beginners

1. **Click the flag** at the top right (🇫🇷 or 🇬🇧)
2. Interface changes language immediately
3. Preference is saved in the browser

**💡 Tip** : Language is automatically detected according to your browser preferences.

#### For Experts

**Translation system** :
- Uses React hook `useTranslation`
- Translations stored in `translations.ts`
- FR/EN support with automatic detection
- Preference saved in localStorage

**Adding new translations** :
1. Add the key in `translations.ts` (both `fr` and `en` sections)
2. Use `t('key')` in components
3. Translation is automatically applied

---

## Troubleshooting

### Greaseweazle Not Detected

**Symptoms** : The "Detect Greaseweazle" button does not find the device.

**Solutions** :
1. **Check USB connection** : Unplug and replug the cable
2. **Check drivers** : Install USB serial drivers if necessary
3. **Check port** : View the list of detected ports to see if the port appears
4. **Test manually** : Run `gw info` from command line to verify connection
5. **Check permissions** : On Linux/macOS, make sure you have permissions to access serial ports

### Error "align command not available"

**Symptoms** : The message "The 'align' command is not available" appears.

**Solutions** :
1. **Check Greaseweazle version** : The `align` command requires v1.23b (PR #592)
2. **Check platform** : v1.23b is currently available only on Windows
3. **Check gw.exe path** : Make sure the path to `gw.exe` is correct
4. **Test from command line** : Run `gw align --help` to verify the command is available

### Read Errors

**Symptoms** : Reads fail or return abnormal values.

**Solutions** :
1. **Check floppy disk** : Make sure the floppy disk is correctly inserted
2. **Check format** : Select the format corresponding to your floppy disk
3. **Check drive** : Test the drive with "Test Drive"
4. **Check Track 0** : Use "Verify Track 0" to diagnose sensor problems
5. **Check connections** : Make sure all cables are properly connected

### Slow Performance

**Symptoms** : Interface is slow or reads take too long.

**Solutions** :
1. **Use Direct Mode** : For faster reads (~150-200ms)
2. **Reduce number of retries** : In automatic mode, reduce the number of retries
3. **Close other applications** : Free up system resources
4. **Check USB connection** : Use a USB 2.0 or higher port
5. **Check browser** : Use a modern and up-to-date browser

### Navigation Problems

**Symptoms** : Track navigation does not work correctly.

**Solutions** :
1. **Check that Greaseweazle is connected** : Indicator should be green
2. **Check selected drive** : Make sure the correct drive is selected
3. **Recalibrate** : Use "Recalibrate (R)" to return to track 0
4. **Check limits** : Make sure the requested track is within format limits

### Display Problems

**Symptoms** : Results do not display or are incorrect.

**Solutions** :
1. **Refresh the page** : Press F5 to reload the interface
2. **Check WebSocket connection** : Open browser console (F12) to see errors
3. **Reset data** : Use "Reset Data" to clean the display
4. **Check browser** : Use a modern browser (Chrome, Firefox, Edge, Safari)

---

## Appendices

### A. Supported Disk Formats

**IBM Formats** :
- ibm.1440 : 1.44 MB (80 tracks, 2 heads, 18 sectors/track)
- ibm.1200 : 1.2 MB (80 tracks, 2 heads, 15 sectors/track)
- ibm.720 : 720 KB (80 tracks, 2 heads, 9 sectors/track)
- ibm.360 : 360 KB (40 tracks, 2 heads, 9 sectors/track)

**Amiga Formats** :
- amiga.amigados : Standard AmigaDOS
- amiga.adf : Amiga Disk File

**Apple Formats** :
- apple2.gcr : Apple II GCR
- mac.gcr : Macintosh GCR

**Commodore Formats** :
- c64.gcr : Commodore 64 GCR

**Other formats** :
- hp.mmfm : HP MMFM
- dec.rx02 : DEC RX02
- And many others defined in `diskdefs.cfg`

### B. Statistics Interpretation

**Alignment percentage** :
- **≥99%** : Excellent, perfect alignment
- **97-98.9%** : Good, acceptable for most uses
- **96-96.9%** : Average, may require adjustment
- **<96%** : Poor, adjustment necessary

**Consistency** :
- **≥90%** : Excellent consistency between reads
- **70-89%** : Good consistency
- **<70%** : Low consistency, may indicate a mechanical problem

**Stability** :
- **≥90%** : Excellent timing stability
- **70-89%** : Good stability
- **<70%** : Low stability, may indicate a mechanical problem

**Azimuth** :
- **Excellent (≥95%)** : Perfectly aligned azimuth
- **Good (85-94%)** : Good azimuth
- **Acceptable (75-84%)** : Acceptable azimuth
- **Poor (<75%)** : Azimuth requiring adjustment

**Asymmetry** :
- **Excellent (≥95%)** : Perfectly symmetrical signal
- **Good (85-94%)** : Good symmetry
- **Acceptable (75-84%)** : Acceptable symmetry
- **Poor (<75%)** : Asymmetry requiring adjustment

### C. Technical References

**Greaseweazle** :
- Official documentation : https://github.com/keirf/greaseweazle
- PR #592 (align command) : https://github.com/keirf/greaseweazle/pull/592

**Panasonic Manual** :
- Section 9.7 : Azimuth analysis
- Section 9.9 : Track 0 verification
- Section 9.10 : Asymmetry analysis

**AlignTester** :
- GitHub repository : https://github.com/Jean-Fred64/AlignTester
- Technical documentation : See `docs/` in the project

### D. Glossary

**Alignment** : Correct positioning of the read/write head relative to floppy disk tracks.

**Azimuth** : Head tilt angle relative to the track. Poor azimuth can cause read errors.

**Asymmetry** : Magnetic signal imbalance. High asymmetry may indicate a mechanical problem.

**Consistency** : Measure of similarity between multiple reads of the same track. Low consistency may indicate a mechanical problem.

**Cylinder** : Set of tracks at the same radial position on all sides. For a double-sided floppy, one cylinder = 2 tracks.

**Flux transitions** : Number of magnetic transitions detected during read. Indicates data density on the track.

**Format** : Data structure of a floppy disk (number of tracks, sectors, etc.). Each floppy type has its own format.

**Track** : Concentric circle on the floppy disk where data is stored. A standard floppy has 80 tracks per side.

**Sector** : Division of a track. A standard track has 18 sectors (for a 1.44 MB floppy).

**Stability** : Measure of timing variation between reads. Low stability may indicate a mechanical problem.

**Track 0** : Outermost track of the floppy disk. Used as reference for positioning.

---

**End of User Guide**
