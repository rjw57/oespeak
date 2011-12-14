#!/usr/bin/env python
# vim: set fileencoding=utf-8

import subprocess
import logging
import hashlib
import os
import sys
from cgi import parse_qs, escape

THIS_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
MP3_CACHE_DIR = os.path.join(THIS_SCRIPT_DIR, 'audio')
ESPEAK_DATA_PATH = THIS_SCRIPT_DIR

# ESPEAK_BIN = '/usr/bin/espeak'
ESPEAK_BIN = os.path.join(THIS_SCRIPT_DIR, 'espeak')
LAME_BIN = '/usr/bin/lame'

class SynthesisError(Exception):
  def __init__(self, msg):
    self.msg = msg

  def __str__(self):
    return self.msg

def speak(text, fp):
  espeak = subprocess.Popen(
      [ESPEAK_BIN, '-v', 'ang',
        '-g', '5', '-s', '160',
        '--path=' + ESPEAK_DATA_PATH,
        '--stdin', '--stdout'],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)

  try:
    with espeak.stdin as f:
      f.write(text)
  except (IOError):
    pass

  lame = subprocess.Popen(
      [LAME_BIN, '-', '-'],
      stdin=espeak.stdout, stdout=fp, stderr=subprocess.PIPE)

  espeak.stdout.close()

  lame_out, lame_err = lame.communicate()
  espeak.wait()

  if espeak.returncode != 0 or lame.returncode != 0:
    logging.error('error synthesising voice:')
    [logging.error('espeak: ' + x.decode('utf-8')) \
        for x in espeak.stderr.readlines()]
    [logging.error('lame: ' + x.decode('utf-8')) \
        for x in lame_err.splitlines()]
    raise SynthesisError('Error running espeak/lame')

def write(text):
  text_bytes = text.encode('utf-8')
  h = hashlib.sha1()
  h.update(text_bytes)
  if not os.path.isdir(MP3_CACHE_DIR):
    os.makedirs(MP3_CACHE_DIR)
  file_name = os.path.join(MP3_CACHE_DIR, h.hexdigest()[:16] + '.mp3')
  if not os.path.exists(file_name):
    with open(file_name, 'wb') as fp:
      speak(text_bytes, fp)
  return file_name

def synth(environ, start_response):
  text = ''

  if environ['REQUEST_METHOD'] == 'POST':
    try:
      request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
      request_body_size = 0
    text = bytes(environ['wsgi.input'].read(request_body_size)).decode('utf-8')
  elif environ['REQUEST_METHOD'] == 'GET':
    query = parse_qs(environ['QUERY_STRING'])
    if 'text' in query:
      text = u' '.join([x.decode('utf-8') for x in query['text']])
  else:
    start_response('500 Internal Server Error', [('Content-type', 'text/plain')])
    return [ 'There was an error processing your request.'.encode('utf-8') ]

  logging.info('Synthesising: ' + text)

  try:
    outfile = write(text[:2000])
  except (SynthesisError):
    start_response('500 Internal Server Error', [('Content-type', 'text/plain')])
    return [ 'There was an error processing your request.'.encode('utf-8') ]

  status = '200 OK'
  headers = [('Content-type', 'audio/mpeg')]
  start_response(status, headers)
  ret = [ open(outfile, 'rb').read() ]

  return ret

def application(environ, start_response):
  if environ['PATH_INFO'] == '/' or environ['PATH_INFO'] == '':
    return synth(environ, start_response)
  start_response('500 Internal Server Error', [('Content-type', 'text/plain')])
  return [ 'There was an error processing your request.'.encode('utf-8') ]

if __name__ == '__main__':
  from wsgiref.util import setup_testing_defaults
  from wsgiref.simple_server import make_server
  logging.basicConfig(level = logging.INFO)
  httpd = make_server('', 8000, application)
  logging.info('Serving on http://localhost:8000/')
  httpd.serve_forever()

