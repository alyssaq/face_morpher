# Face Morpher

Warp, average and morph human faces!

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

## To morph between 2 images:
Must supply path to source and destination image. Optional blend of the 2 images

    python transformer/morpher.py --src=<src_imgpath> --dest=<dest_imgpath> [--blend]

## To average all images in a folder:

    python mass_morpher.py --data=../data --images=<images_folder> [--blend]

## Help

    python mass_morpher.py -h

## Documentation (requires sphinx)

    ./make_docs.sh