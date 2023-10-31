#!/usr/bin/python3
import sys
import re


TIME_FORMAT_REGEX = re.compile(r'(\d+):(\d+):(\d+):(\d+)')
ARGS_NUMBER = 4
USAGE_MESSAGE = 'Uso: times_sum.py cam_time gmp_time time_to_add'
NOT_VALID_FORMAT_ERROR_MESSAGE = 'Error: Los tiempos deben estar en el formato "hh:mm:ss:ff"'


def gameplay_times_sum(cam_time, gmp_time, time_to_add):
    if not TIME_FORMAT_REGEX.match(cam_time) \
          or not TIME_FORMAT_REGEX.match(gmp_time) \
          or not TIME_FORMAT_REGEX.match(time_to_add):
        print(NOT_VALID_FORMAT_ERROR_MESSAGE)
        return

    # get times from parms
    cam_hurs, cam_mins, cam_secs, cam_frames = map(int, cam_time.split(':'))
    gmp_hours, gmp_mins, gmp_secs, gmp_frames = map(int, gmp_time.split(':'))
    hours_to_add, mins_to_add, secs_to_add, frames_to_add = map(int, time_to_add.split(':'))
    # get total frames
    cam_total_frames = (cam_hurs*60*60*30 + cam_mins*60*30 + cam_secs*30 + cam_frames)
    gmp_total_frames = (gmp_hours*60*60*30 + gmp_mins*60*30 + gmp_secs*30 + gmp_frames)
    total_frames_to_add = (hours_to_add*60*60*30 + mins_to_add*60*30 + secs_to_add*30 + frames_to_add)
    
    # cam sum
    cam_new_total_frames = cam_total_frames + total_frames_to_add
    cam_new_hours, cam_new_total_frames = divmod(cam_new_total_frames, 30 * 60 * 60)
    cam_new_mins, cam_new_total_frames = divmod(cam_new_total_frames, 30 * 60)
    cam_new_secs, cam_new_frames = divmod(cam_new_total_frames, 30)
    # gmp sum
    gmp_new_total_frames = gmp_total_frames + total_frames_to_add
    gmp_new_hours, gmp_new_total_frames = divmod(gmp_new_total_frames, 30 * 60 * 60)
    gmp_new_mins, gmp_new_total_frames = divmod(gmp_new_total_frames, 30 * 60)
    gmp_new_secs, gmp_new_frames = divmod(gmp_new_total_frames, 30)

    # results
    ffmpeg_time_to_add = f"{hours_to_add:02d}:{mins_to_add:02d}:{secs_to_add:02d}.{frames_to_add:02d}"
    ffmpeg_cam_time = f"{cam_hurs:02d}:{cam_mins:02d}:{cam_secs:02d}.{cam_frames:02d}"
    ffmpeg_gmp_time = f"{gmp_hours:02d}:{gmp_mins:02d}:{gmp_secs:02d}.{gmp_frames:02d}"
    ffmpeg_cam_new_time = f"{cam_new_hours:02d}:{cam_new_mins:02d}:{cam_new_secs:02d}.{cam_new_frames:02d}"
    ffmpeg_gmp_new_time = f"{gmp_new_hours:02d}:{gmp_new_mins:02d}:{gmp_new_secs:02d}.{gmp_new_frames:02d}"
    print('    +', ffmpeg_time_to_add)
    print('cam :', ffmpeg_cam_time, '->', ffmpeg_cam_new_time)
    print('gmp :', ffmpeg_gmp_time, '->', ffmpeg_gmp_new_time)


if __name__ == "__main__":
    if len(sys.argv) != ARGS_NUMBER:
        print(USAGE_MESSAGE)
    else:
        cam_time, gmp_time, time_to_add = sys.argv[1], sys.argv[2], sys.argv[3]
        gameplay_times_sum(cam_time, gmp_time, time_to_add)
