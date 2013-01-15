import Event

if __name__ == '__main__':
  import sys
  for line in sys.stdin:
    print(str(Event.decode_event(line)))
