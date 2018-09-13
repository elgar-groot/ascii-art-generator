import sys
import numpy as np
from PIL import Image
import glob
import os


def find_best_match(block_factor, glyphs):
	best_match_score = sys.maxint
	for ascii_code in glyphs:
		score = abs(block_factor - glyphs[ascii_code])
		if score < best_match_score: # lower score is better
			best_match = ascii_code
			best_match_score = score
	return best_match

def main():
	print(len(sys.argv))
	if len(sys.argv) < 3 or len(sys.argv) > 4:
		print("Usage: python generate_ascii_art.py <path to glyphs directory> <path to image> [<resolution>]")
		print("The first argument should be a path to a folder containing images of individual ascii characters, of which the name is the ascii code.")
		print("  so for example a picture of an 'a' should be stored as 97.jpg.")
		print("The second argument is the image to convert to ascii art.")
		print("The third argument (optional) sets the resolution for the output. A lower number gives a higher resolution. Default is 2.")
		print("")
		print("Usage example: python generate_ascii_art.py ./glyphs ./image.jpg 1")
		return
	
	if len(sys.argv) == 4 and int(sys.argv[3]) >= 1:
		blocksize_factor = int(sys.argv[3])
	else:
		blocksize_factor = 2
	
	blocksizex = 2 * blocksize_factor
	blocksizey = 1 * blocksize_factor

	# Initialize glyphs
	glyphs = {}
	min_gl = 255
	max_gl = 0
	for name in glob.glob(os.path.join(sys.argv[1], "*.jpg")):
		ascii_code = os.path.splitext(os.path.basename(name))[0]
		glyph_array = np.array(Image.open(name).convert('L'))
		glyph_avg = np.average(glyph_array)
		if glyph_avg > max_gl:
			max_gl = glyph_avg
		if glyph_avg < min_gl:
			min_gl = glyph_avg
		glyphs[ascii_code] = np.average(glyph_array)

	# Caclculate normalized values (between 0-1)
	for g in glyphs:
		glyphs[g] = (glyphs[g] - min_gl) / (max_gl - min_gl)
		
	# Load image
	img = Image.open(sys.argv[2]).convert('L') # 'convert('L') converts to grayscale
	img_array = np.asarray(img, np.uint8)
	# img.show()

	(imgx,imgy) = img_array.shape
	rows = imgx/blocksizex
	columns = imgy/blocksizey
	# print("Image size: {}".format(img_array.shape))
	# print("rows: {}, columns: {}".format(rows, columns))

	# Calculate averages for the blocks
	image_avgs = np.zeros((rows, columns))
	for row in range(0,imgx-blocksizex,blocksizex):
		for col in range(0,imgy-blocksizey,blocksizey):
			block = img_array[row:row+blocksizex, col:col+blocksizey]
			image_avgs[row/blocksizex, col/blocksizey] = np.average(block)

	image_tmp = image_avgs - np.min(image_avgs)
	image_norm = image_tmp / np.max(image_tmp)

	# Match and write out ascii characters
	for row in range(rows):
		for col in range(columns):
			best_match = find_best_match(image_norm[row, col], glyphs)
			sys.stdout.write(chr(int(best_match)))
			sys.stdout.flush()
		sys.stdout.write("\n")
		sys.stdout.flush()

if __name__ == "__main__":
	main()