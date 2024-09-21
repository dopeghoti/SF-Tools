#!/usr/bin/env python3
from typing import Union, Dict
import os
from dotenv import load_dotenv
from dotenv import set_key

class ConfigManager():
    def __init__(self):
        self.config = {}
        try:
            load_dotenv( dotenv_path = './.env' )
            self.config['DISCORD_TOKEN']  = os.getenv( 'DISCORD_TOKEN'   )
            self.config['DISCORD_GUILD']  = int( os.getenv( 'DISCORD_GUILD'   ) )
            self.config['DISCORD_STATUS_CHANNEL']   = os.getenv( 'DISCORD_STATUS_CHANNEL' )
            self.config['SATISFACTORY_TOKEN']  = os.getenv( 'SATISFACTORY_TOKEN' )
            self.config['SATISFACTORY_HOST']   = os.getenv( 'SATISFACTORY_HOST' )
            self.config['SATISFACTORY_PORT']   = int( os.getenv( 'SATISFACTORY_PORT' ) )
            self.config['SATISFACTORY_IPv6']    = bool( os.getenv( 'SATISFACTORY_IPv6' ) )
        except TypeError as e:
            print( f'Error reading `dotenv`: {e}' )

    def get(self, key: str = None) -> Union [ int, str, bool ]:
        try:
            return self.config[key]
        except KeyError as e:
            print( f'Error attempting to read unknown configuration key {key}.' )
            return False

    def set( self, key: str, value: Union [ int, str, bool ] ) -> bool:
        if isinstance( value, int):
            value = str(value)
        if key is None or value is None:
            raise ValueError( f'Attempt to improperly set config {key=} to {value=}.' )
        if isinstance( value, str ):
            qm = 'always'
            if value.isnumeric():
                if value[:].isdigit():
                    qm = 'never'
                else:
                    raise ValueError( f'Attempted to set integer configuration {key} to non-integer {value}.' )
        if set_key( dotenv_path = './.env', key_to_set = key, value_to_set = value, quote_mode = qm ):
            return True
        else:
            return False

def main() -> None:
    import sys
    try:
        raise NotImplementedError( 'bot_config.py should not be executed directly.' )
    except NotImplementedError as e:
        print( f'{e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
