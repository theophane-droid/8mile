import os

from .__version__ import __version__, __author__


RABBIT_BANNER =  """
  ______         .__.__                                      .___            
 /  __  \  _____ |__|  |   ____   _______   ____   ____    __| _/___________ 
 >      < /     \|  |  | _/ __ \  \_  __ \_/ __ \ /    \  / __ |/ __ \_  __ \\
/   --   \  Y Y  \  |  |_\  ___/   |  | \/\  ___/|   |  \/ /_/ \  ___/|  | \/
\______  /__|_|  /__|____/\___  >  |__|    \___  >___|  /\____ |\___  >__|   
       \/      \/             \/               \/     \/      \/    \/     
** Hmilerender v{} by {}**
""" .format(__version__, __author__)


if not 'HMILE_BANNER' in os.environ or os.environ['HMILE_BANNER'] != 'disable':
    print(RABBIT_BANNER)