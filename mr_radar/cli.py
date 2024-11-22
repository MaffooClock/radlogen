# coding: utf-8

import argparse
from pathlib import Path
from loguru import logger


from .rlg_exception import *

def main():

    parser = argparse.ArgumentParser(
        description='Generate a base map or series of NEXRAD radar frames that can be overlayed on the base map'
    )

    parser.add_argument(
        'command',
        choices=[ 'map', 'frames', 'dump-products' ],
        help='The command to specify whether to generate the base map or NEXRAD radar imagery frames, or dump a list of available radar products for the given site'
    )

    parser.add_argument(
        'site_id',
        metavar='SITE',
        help='The four-letter site ID on which to center the imagery'
    )

    parser.add_argument(
        '-r', '--radius',
        type=int,
        dest='radius',
        help='The distance in miles around the radar site to map'
    )

    parser.add_argument(
        '-P', '--path',
        type=Path,
        dest='path',
        help='The destination path to the generated images.  Defaults to "./out" in current working directory.'
    )

    parser.add_argument(
        '-f', '--file',
        dest='name',
        help='The name of the output file.  Default is "map.png" for the map command, or "frame_<i>.png" for the frames command.'
    )

    parser.add_argument(
        '-n', '--frames',
        type=int,
        dest='frames',
        help='The number of NEXRAD radar image frames to generate (default: 12)'
    )

    parser.add_argument(
        '-p', '--product',
        type=str,
        dest='product',
        help='The radar product to use for generating NEXRAD frames (default: Reflectivity)'
    )

    args = vars( parser.parse_args() )
    command = args.pop('command')
    generator = None

    try:

        if command == 'map':
            args.pop( 'frames' )
            args.pop( 'product' )

            from .map_generator import MapGenerator
            generator = MapGenerator( **args )

        elif command in [ 'frames', 'dump-products' ]:
            from .frame_generator import FrameGenerator
            generator = FrameGenerator( **args )

            if command == 'dump-products':
                generator.dump_products()
                generator = None

        if generator:
            generator.generate()

    except RLGException as e:
        logger.error( "Image generation aborted: {}", e )

    except Exception as e:
        if generator:
            logger.error(
                "💥 KA-BOOM! 💥"
                "\n"
                "\tSite:        {site_id}       \n"
                "\tSite Coords: {site_coords}   \n"
                "\tRadius:      {radius}        \n"
                "\tBBox:        {image_bbox}    \n"
                "\tEnvelope:    {image_envelope}\n"
                "\tFile Path:   {file_path_name}\n",

                site_id        = generator.site_id,
                site_coords    = generator.site_coords,
                radius         = generator.radius,
                image_bbox     = generator.image_bbox,
                image_envelope = generator.image_envelope,
                file_path_name = generator.file_path_name
            )

        raise

if __name__ == '__main__':
    main()