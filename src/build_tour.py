"""Create a transparent, three-minute screenshot-based tour with macOS narration.

This is not a continuous screen recording or the project owner's recorded voice.
All browser captures show the actual published application.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
os.environ.setdefault('MPLCONFIGDIR',str(Path('.local/matplotlib').resolve()))
from matplotlib import get_data_path

SECTIONS=[
 ('01-executive-overview.png',25,'01  |  The management decision',
  'Which permit categories should operations investigate first?',
  'Permit Ops answers one operations question: which Toronto permit categories merit investigation? This project uses six hundred forty nine thousand, three hundred seventy six real City of Toronto records. Python and PostgreSQL prepare the evidence, and this browser dashboard works on a Mac. This tour uses actual dashboard captures and computer generated narration.'),
 ('01-executive-overview.png',30,'02  |  Read the population first',
  'Nov 2025–Oct 2026: 35,876 eligible issues · 28-day median · 141-day P90',
  'The default window is November twenty twenty five through October twenty twenty six. There are thirty seven thousand seventy four eligible applications and thirty five thousand eight hundred seventy six issues. These are different lifecycle cohorts, not a conversion rate. Median review time is twenty eight calendar days. The ninetieth percentile is one hundred forty one days. Both measures matter because a stable typical case can hide a changing long tail.'),
 ('02-bottleneck-analysis.png',35,'03  |  Compare severity, scale and change',
  'New Building: median 79 days, P90 866 days; the prior median was 155.5 days.',
  'Bottleneck analysis compares duration with volume and an equally long preceding period. New Building has two hundred thirty one recent issues, a seventy nine day median, and an eight hundred sixty six day ninetieth percentile. Its median decreased from one hundred fifty five point five days, so calling the whole category worsening would be misleading. These elapsed times include applicant responses and case complexity. They cannot establish staff performance or a specific cause.'),
 ('02-bottleneck-analysis.png',40,'04  |  Investigate New Houses',
  'Original permits: 53% of issues, but 131 of 151 reviews over a year. Q1 2026 contains 119.',
  'The New Houses deep dive looks inside the category. Its recent cohort has one thousand four hundred forty six issues, a fifty two day median, and a four hundred nineteen point five day ninetieth percentile. Original permits account for about fifty three percent of issues, but one hundred thirty one of the one hundred fifty one reviews over a year. Their median stayed at seventy one days while their ninetieth percentile rose from four hundred twenty eight point eight to eight hundred seventy six days. First quarter twenty twenty six contains one hundred nineteen long reviews. This suggests a focused case audit, not a proven explanation.'),
 ('03-active-workload.png',30,'05  |  Separate open from unissued',
  '194,325 active permits · 13,580 unissued · median unissued age 426 days',
  'Active workload is a snapshot across all application years. There are one hundred ninety four thousand three hundred twenty five active permits. Only thirteen thousand five hundred eighty are unissued, about seven percent. Issued cases can still be in construction or inspection. Median unissued age is four hundred twenty six days. Validate old statuses before treating this as review backlog. Historical date controls are disabled here.'),
 ('03-active-workload.png',20,'06  |  Make a defensible recommendation',
  'Audit cases, validate status history, then track P90 and unresolved age together.',
  'Conflicting identities are quarantined. SQL and interface tests support the report. Audit original New Houses cases and the first quarter issuance concentration. Track long reviews alongside unresolved ages. These patterns do not prove causes.')
]


def build():
    root=Path('.local/tour');root.mkdir(parents=True,exist_ok=True)
    output=Path('dashboard/recordings');output.mkdir(parents=True,exist_ok=True)
    encoder=imageio_ffmpeg.get_ffmpeg_exe()
    font_root=Path(get_data_path())/'fonts/ttf'
    regular=ImageFont.truetype(str(font_root/'DejaVuSans.ttf'),23)
    bold=ImageFont.truetype(str(font_root/'DejaVuSans-Bold.ttf'),29)
    small=ImageFont.truetype(str(font_root/'DejaVuSans.ttf'),17)
    width,height=1440,1020
    records=[]
    for i,(image_name,duration,title,caption,narration) in enumerate(SECTIONS):
        original=Path('dashboard/screenshots')/image_name
        frame=Image.new('RGB',(width,height),'#f5f7fb');draw=ImageDraw.Draw(frame)
        draw.rectangle((0,0,width,65),fill='#14283e')
        draw.text((35,17),title,font=bold,fill='white')
        shot=Image.open(original).convert('RGB');shot.thumbnail((1380,790),Image.Resampling.LANCZOS)
        frame.paste(shot,((width-shot.width)//2,76))
        draw.rectangle((0,878,width,height),fill='#14283e')
        words=caption.split();lines=[];line=''
        for word in words:
            candidate=(line+' '+word).strip()
            if draw.textlength(candidate,font=regular)>1360:lines.append(line);line=word
            else:line=candidate
        if line:lines.append(line)
        for j,line in enumerate(lines):draw.text((35,894+j*31),line,font=regular,fill='white')
        draw.text((35,985),'Actual dashboard captures · Screenshot-based tour · Computer-generated narration · Snapshot 11 Nov 2026',font=small,fill='#a8bfd6')
        png=root/f'section-{i}.png';frame.save(png)
        text=root/f'section-{i}.txt';text.write_text(narration)
        audio=root/f'section-{i}.aiff'
        subprocess.run(['say','-v','Daniel','-r','185','-f',str(text),'-o',str(audio)],check=True)
        probe=subprocess.run([encoder,'-hide_banner','-i',str(audio)],capture_output=True,text=True)
        match=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',probe.stderr)
        if not match:raise RuntimeError('Could not verify narration duration')
        h,m,s=map(float,match.groups());seconds=h*3600+m*60+s
        if seconds>duration:raise ValueError(f'Section {i+1} narration exceeds its {duration}-second window: {seconds}')
        clip=root/f'section-{i}.mp4'
        result=subprocess.run([encoder,'-y','-loglevel','error','-loop','1','-framerate','10','-i',str(png),
           '-i',str(audio),'-t',str(duration),'-vf','format=yuv420p','-af','apad',
           '-c:v','libx264','-preset','fast','-crf','24','-c:a','aac','-ar','44100','-b:a','96k',
           '-map_metadata','-1',str(clip)],capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stderr[-2000:])
        records.append({'section':i+1,'seconds':duration,'narration_seconds':seconds,
                        'source_capture':str(original),'source_sha256':hashlib.sha256(original.read_bytes()).hexdigest()})
        print(f'Rendered section {i+1}/6 ({duration}s)',flush=True)
    listing=root/'clips.txt';listing.write_text('\n'.join(f"file '{(root/f'section-{i}.mp4').resolve()}'" for i in range(len(SECTIONS))))
    target=output/'PermitOps_3_Minute_Manager_Tour.mp4'
    subprocess.run([encoder,'-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),
                    '-c','copy','-movflags','+faststart',str(target)],check=True)
    probe=subprocess.run([encoder,'-hide_banner','-i',str(target)],capture_output=True,text=True)
    match=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',probe.stderr)
    if not match:raise RuntimeError('Video duration unavailable')
    h,m,s=map(float,match.groups());seconds=h*3600+m*60+s
    assert abs(seconds-180)<.2,seconds
    # Decode a frame from each section as a final media-integrity check.
    for i,offset in enumerate([2,27,57,92,132,162]):
        subprocess.run([encoder,'-y','-loglevel','error','-ss',str(offset),'-i',str(target),
                        '-frames:v','1',str(root/f'verified-frame-{i}.png')],check=True)
    manifest={'video':str(target),'seconds':seconds,'bytes':target.stat().st_size,
              'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'sections':records,
              'computer_generated_narration':True,'continuous_screen_recording':False,
              'six_sample_frames_decoded':True}
    Path('outputs/tour_manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({k:v for k,v in manifest.items() if k!='sections'},indent=2))


if __name__=='__main__':build()
