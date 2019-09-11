import unittest

import ear

class TestMatrix(unittest.TestCase):
	def test_matrix(self):
		matrix = ear.Matrix(2, 3, None)
		self.assertEqual([None, None, None, None, None, None], matrix.flatten())

		matrix.fill([
			[1, 2, 3],
			[4, 5, 6]
		])

		self.assertEqual([1, 2, 3], matrix.get_input_vector(0))

		self.assertEqual(6, len(matrix.flatten()))
		self.assertEqual([1, 2, 3, 4, 5, 6], matrix.flatten())

		matrix.set_output_vector(0, [7, 8])
		self.assertEqual([7, 2, 3, 8, 5, 6], matrix.flatten())


if __name__ == '__main__':
	unittest.main()
