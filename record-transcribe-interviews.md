# How to record and transcribe interviews

[//]: # (https://confluence.sys.kth.se/confluence/x/lRDgEQ)

This guide is a complement to the [Interview studies: good research data management practices](../../methodologies/interview-practices.md)
article, which you might want to read first.

On this page you can find practical guides for recording and transcribing using
digital tools and services via KTH IT-provided platforms such as Zoom, Play, MS365/Copilot,
national research infrastructure or locally installed software on your own device.
Notes are provided for information that is relevant for assessing the risks related
to data transfer and information security.

There are many factors that may influence what workflow that is most suitable for
a specific use case, for instance how interviews were recorded and if you have
a few or very many audio/video recordings; multiple persons speaking or a single person;
what language that is spoken; etc.


## Record an online interview using KTH Zoom

!!! note "Zoom's storage locations"
    In KTH's Zoom service the default data storage location is the Zoom cloud
    storage provider, which stores data at Nordunet's data centers in the Nordic
    countries.
    But if you use the caption functionality in Zoom the data will also be transferred
    to several [Zoom third-party subprocessors](https://www.zoom.com/en/trust/subprocessors).
    Transcribing using automatic real-time captions in Zoom is therefore
    **not recommended** for privacy-sensitive interviews. You can reduc
    data transfer to third parties further by selecting a local storage option and
    disabling captions when setting up your interview meeting.
    However by keeping the default cloud storage, the recorded files are transferred
    to SUNET Play/Kaltura (Kaltura is the Play service at KTH) as one of the
    NORDunet on-premise media management services, so data is kept within Nordunet
    and this makes it easy to use the transcription features in KTH Play, see below.

1. **Check settings before you schedule the interview meeting(s) in Zoom**:
   Go to your profile in the Zoom-client and click on "Settings" -> "Recording"
   in the menu to select where recorded files will be stored.
   Our recommendation is to choose an encrypted storage space available for
   you - if you choose local storage also check that you have sufficient free
   storage space on disk.
   By default, storage will be the Zoom Cloud storage.
   Consider the optional settings: do you want to display filenames and timestamp
   in the video recording? You could enable captions and get an auto-transcript
   - but in that case the recorded information will be processed and possibly stored
   by third-party services. Is this OK for the interviewee under informed consent?
    Under the Advanced recording settings, you can also select separate audio-files
    for different participants which is a good choice for later transcription or annotation.
2. **Before recording, make sure that you ask for and receive informed consent**
   from the interviewee to record the interwiew.
   The consent can be documented either via a separate document or by recording the consent.
3. **When recording, make sure you and the person(s) to be interviewed have a stable internet-connection**
   to ensure a high-quality recording. If the recording occurs under unstable conditions,
   an option that can improve audio/video quality is that the interviewee records
   the interview on his/her device and sends the audio/video files to you afterwards
   using an end-to-end encrypted file-sharing service. For this to work you need
   to make the interviewee co-host.
4. **After the end of the interview**
   the audio/video files can be transferred to a separate transcription service
   - see more on transcription below.


An example on how to inform informants/interviewees on data processing:

> Interviews will be performed via the digital video meeting platform Zoom
> and recordings of the interviews will be processed at the Zoom-platform
> and via Zoom sub-processors. Recordings and transcripts will be kept at
> access-controlled storage/at KTH local storage/at storage service procured by KTH.


## Transcribe recorded Zoom-interviews using KTH Play with SUNET Scribe as integrated service

[KTH Play](https://play.kth.se) (SUNET Play/Kaltura) is an internal service platform
for uploading, watching and transcribing video recordings. The KTH Play service
is procured via SUNET and media-files will be stored on Nordunet data centers.
If you use KTH Zoom Cloud storage, the default storage for your recordings will
be accessible in KTH Play.

You can also upload files to KTH Play and use the built-in version of SUNET Scribe
for transcription. SUNET Scribe is based on Whisper LLM and variants of Whisper
optimized for Swedish and Norwegian languages.
SUNET Scribe is hosted at SUNET data centers in Sweden -
[read more in SUNETs wiki](https://wiki.sunet.se/pages/viewpage.action?pageId=281641283).

If you prefer video instructions for how to transcribe using KTH Play, see the video
linked from [this KTH Intranet page](https://intra.kth.se/en/it/video/texta/i-kth-play-reach).

1. If you saved your recordings in the Zoom Cloud storage at Nordunet, you can find
   the recordings when logging in at KTH Play. If you saved files locally, you can
   upload those files to KTH Play.
2. Login to KTH Play and go to your profile in upper right corner and click on "My media files".
3. You will get a list of all your recorded media files, click on the title for
   the file you would like to transcribe.
4. Below the media file, you can see an **Actions** drop-down menu.
5. Click on the Actions menu and select "Captions and enrich" and then on "order".
6. When the transcription is ready, you can click on edit to manually check the
   machine-translation or export the transcript file.
7. At the end of your project, you can transfer media-files and transcripts for archiving.


## Transcribe multiple interviews using the stand-alone Sunet Scribe web-interface with additional encryption

1. Go to <https://scribe.sunet.se>
2. Login with KTH SSO.
   If you do not yet have access, contact KTH IT Support to get added to the user group
   for Sunet Scribe.
3. Set a passphrase. Note: If you forget your passphrase, you will **not be able**
   to access the recordings and transcripts. It is a good idea to use a password manager.
[//]: # (I considered linking to my own note on password managers, but it suffers from lots of broken links https://links.solarchemist.se/shaare/pWkikg)
4. Click on the **Upload** button and upload all the file recordings.
5. Click on **Transcribe**.
6. When the transcription is done, you can optionally edit the text manually
   before saving the transcripts in a suitable file format by *export*ing.
   Note: Sunet Scribe is intended for temporary processing only. When you are done,
   you should delete the recordings *and* transcripts from SUNET Scribe, so they are
   not stored there longer than necessary. But make sure to save them in a suitable
   KTH-provided storage for at least ten years. If you do not delete them from
   SUNET Scribe yourself, the system will auto-deleted them after a certain time.


## Transcribing multiple interviews and processing transcripts with Whisper at UPPMAX for sensitive data

This is a solution suitable of you have a very large collection of material containing
sensitive personal information. Then you can use Whisper LLM accessible via NAISS
supercomputing facilities for sensitive data in Uppsala.

1. Apply for an account at SUPR at NAISS, the National infrastructure for super-computing
   here: <https://supr.naiss.se/person/register>
2. When you have received your account, follow the instructions here:  
   <https://docs.uppmax.uu.se/software/whisper>

Note that if you only have interview material in Swedish but in many different dialects,
[KB Whisper](https://kb-labb.github.io/posts/2025-03-07-welcome-KB-Whisper/index.html)
may be an option.
[//]: # (But how accessible is KB Whisper? And what do we mean by "accessible" here?)

You can also download and use Whisper on a local device - but then you are responsible
for ensuring data does not leak and there is no support on how to do it, so you need
to be able to handle it on your own.


## Transcribing interviews using speech-to-text models locally on your own device

As long as you find a good model that works for your use case and are aware of
standard cybersecurity hygiene practices for maintaining your own device this may
be a suitable option for you.

Whisper is currently one of the most common open source speech-to-text models, but
there are other alternatives as well, as well as variants of Whisper such as the
[KB Whisper model fine-tuned for Swedish](https://huggingface.co/KBLab/kb-whisper-large).
Whisper is reported to work well with English and Swedish individual speech, but
may be less suited for multiple-speaker settings and for certain under-represented
languages.

For other European languages, consider the [European Commission's Multi-Lingual Services](https://language-tools.ec.europa.eu) or the EU-based company [Tilde](https://tilde.ai/tildeopen-llm).

Ollama is a well-known package that you can download for MacOS, Linux and Windows
where you can run many different LLMs locally - see the different models available
when using Ollama here <https://ollama.com/search>.

If it is important for your study design to obtain precise timestamps,
[Easy Transcriber](https://kb-labb.github.io/easytranscriber) by KB is a freely licensed
software you can download and install locally on MacOS, Linux and Windows.

!!! note "Be aware of risks when managing your own device"
    Be aware of the risks associated with being responsible for your own device.
    The development of new and updated models is rapid and you may find more models
    at HuggingFace and other platforms, but it is hard to do a good and thorough
    assessment on usefulness, risks and security without spending too much time on that.
    Make sure you have good routines for updating, patching, backup and do not leave
    network ports open, bluetooth on, etc., when not necessary, and avoid
    clicking on suspicious links, etc.


## Manually transcribing a few recorded interviews using oTranscribe

oTranscribe is an online tool for **manual** transcription where the data is stored
in your web browser's cache, so it never leaves your computer.
You can use the service to manually transcribe audio/video recordings.

1. Go to <https://otranscribe.com>
2. Click on the **Start transcribing** button.
3. Choose your audio or video file. You can use keyboard shortcuts to pause, play,
   rewind and forward in the recording while writing your transcription.
4. When you are done  with transcribing, copy your text and paste it into a document
   that you can store in a document storage option suitable for your use case.


## Recording an online interview using "KTH Teams" and further processing in MS365 and other services on the Microsoft platform

Note that KTH Teams is part of the Microsoft Cloud platform services procured by
KTH IT that provides online meeting, recording and captions functionality.
According to the service provider agreement, audio/video recordings will be stored
and processed either within Sweden (no captions) or within Europe (with captions).
Captioning relies on Azure AI services. This also appears to be true for using
dictate/transcribe functions in MS365. Recording and transcribing using Teams or MS365
is not recommended for privacy-sensitive interviews where access for US government
is perceived as a risk to the individuals interviewed.

1. **Check the settings**.
   Most settings are fixed - for instance, you cannot change storage location or
   enable timestamps. Recordings will be stored on your Microsoft account in Sharepoint.
2. **Before recording, make sure that you ask for and is given an informed consent**
   from the interviewee to record the interview and for how data will be processed.
3. **When recording, make sure you and the person(s) to be interviewed have a stable internet-connection to ensure high-quality of the recording**
   If the person you will interview have a shaky Internet connection and only
   a guest Teams account, Zoom may be a better option(?).
[//]: # (Would Zoom be a better option? We seem unsure about this?)
4. **After the end of the interview** transfer the audio/video files to a separate
   transcription service if you did not enable captions and save the caption file.
   Transcriptions can also be generated in Sharepoint for the recorded media file
   after the end of the interview. The transcript can be used in Sharepoint as captions
   or downloaded as a transcript in Word or Vtt format.
5. **After processing and analysing**
   Please note: the media files will remain retrievable from your Microsoft account
   for 60 days after deleting the files from your Sharepoint/Onedrive.
    If you started the Teams meeting from a shared Teams storage space you will **not**
    be able to delete files permanently. This may or may not be problematic depending
    on if you are bound to conditions for how to store and share data in an ethical permit.
    In addition, there is a risk of data loss if data is stored on a personal account
    belonging to a PhD student or postdoc that leaves KTH. Make sure to archive
    the media files, transcripts and documentation at [KTH Data Repository](https://datarepository.kth.se)
    before they leave KTH.


!!! note "Handling of more sensitive personal information"
    If you conduct interviews where more sensitive personal information is exposed
    you need to take extra security measures in order to protect the personal integrity
    of the individuals that are interviewed. Especially consider the principle of
    not sharing such information more than necessary, for example with third-party
    service providers or third-party persons and ensure that files are encrypted
    both at rest and during transfer.
    For now, contact <dataskydd@kth.se>!

    <!--
    + To find a suitable storage option for media files and transcribed documents,
      see the overview of KTH storage options.
      [Var kan jag som KTH forskare lagra data? Översikt lagringsalternativ - olika användningsområden olika delar av forskningslivscykeln](https://confluence.sys.kth.se/confluence/x/O4EPEQ)
    -->

    + For *annotation* of audio/video files rather than transcription, one option is
      to do this on your local device by installing
      [ELAN (available for Linux, macOS, Windows)](https://archive.mpi.nl/tla/elan/download).
    + The Swedish National Data Service (SND) has guides and information about tools
      for finding and removing personal information from transcript, see more here:  
      <https://researchdata.se/en/manage-data/data-containing-personal-information>
    + Read more on privacy issues that may occur when conducting interviews here:  
      <https://utrechtuniversity.github.io/dataprivacyhandbook/interview-scenario.html#interview-scenario>
