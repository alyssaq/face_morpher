# Face Morpher

## Steps

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
  
  * Morpher a collection of images

#### Blender

  * Optional blending of warped image:
  * Weighted average
  * Alpha feathering
  * Poisson blend

## To run:

    cd transformer/
    python mass_morpher.py --data=../data --images=<images_folder> [--blend]

## Help

    python mass_morpher.py -h

## Documentation (requires sphinx)

    ./make_docs.sh