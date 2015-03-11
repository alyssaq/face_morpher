# Face Morpher

Warp, average and morph human faces!

## To morph between 2 images:
Must supply path to source and destination image.

    python transformer/morpher.py --src=<src_imgpath> --dest=<dest_imgpath>

All options listed in `morpher.py` (pasted below):
```
Morph from source to destination face

Usage:
  morpher.py --src=<src_path> --dest=<dest_path>
            [--width=<width>] [--height=<height>]
            [--num=<num_frames>] [--fps=<frames_per_second>]
            [--out_frames=<folder>] [--out_video=<filename>]
            [--plot] [--blend] [--data=<classifiers_folder>]

Options:
  -h, --help              Show this screen.
  --src=<src_imgpath>     Filepath to source image (.jpg, .jpeg, .png)
  --dest=<dest_path>      Filepath to destination image (.jpg, .jpeg, .png)
  --width=<width>         Custom width of the images/video [default: 500]
  --height=<height>       Custom height of the images/video [default: 600]
  --num=<num_frames>      Number of morph frames [default: 20]
  --fps=<fps>             Number frames per second for the video [default: 10]
  --out_frames=<folder>   Folder path to save all image frames [default: None]
  --out_video=<filename>  Filename to save a video [default: None]
  --plot                  Flag to plot images [default: False]
  --blend                 Flag to blend images [default: False]
  --data=<folder>         Folder to .xmls for classifiers [default: data]
  --version               Show version.
```
## To average all images in a folder:

    python mass_morpher.py --images=<images_folder> [--blend]

## Steps (transformer folder)

#### 1. Locator

 * Locates face points (using stasm)
 * For a different locator, return an array of (x, y) control face points

#### 2. Aligner

  * Align faces by resizing, centering and cropping to given size

#### 3. Warper

  * Given 2 images and its face points, warp one image to the other
  * Triangulates face points
  * Affine transforms each triangle with bilinear interpolation

#### 4. Morpher
  
  * Morph between 2 images

#### Blender

  * Optional blending of warped image:
  * Weighted average
  * Alpha feathering
  * Poisson blend

## Documentation (requires sphinx)

    ./make_docs.sh

## License
[MIT](http://alyssaq.github.io/mit-license/)