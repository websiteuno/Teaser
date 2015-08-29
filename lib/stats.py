#!/usr/bin/env python
class ReferenceMappingStatistics:
	def __init__(self):
		# Main statistics (Sum up to total)
		self.correct = 0  # Num. of correctly mapped query sequences
		self.wrong = 0  # Num. of wrongly mapped query sequences (different region or pos diff over threshold)
		self.not_mapped = 0  # Num. of unmapped query sequences
		self.not_found = 0  # Num. of sequences that were not found in the self output (fatal if > 0)

		# Extra statistics
		self.total = 0  # Actual number of reads (in reference mapping)
		self.total_testee = 0  # Number of reads in mapper output (includes secondary alignments)
		self.ignored_testee = 0
		self.reverse = 0
		self.not_found_comparison = 0

		self.wrong_chromosome = 0
		self.wrong_pos = 0

		self.precision = 0
		self.recall = 0
		self.fmeasure = 0

		# Additional data
		self.failed_rows = []

		self.mapq_cumulated = {}
		for i in range(256):
			self.mapq_cumulated[i] = {"correct": 0, "wrong": 0}

		# Placeholders
		self.maptime = -1

	def to_string(self):
		return self.to_csv()

	def to_csv(self):
		result = "correct,wrong,not_mapped,not_found,not_found_comparison,total,reverse,secondary,precision,recall,fmeasure\n"
		result += ",".join([str(e) for e in
							[self.correct, self.wrong, self.not_mapped, self.not_found, self.not_found_comparison,
							 self.total, self.reverse, self.ignored_testee, self.precision, self.recall,
							 self.fmeasure]])
		return result

	def computeMeasures(self):
		try:
			self.precision = float(self.correct) / float(self.correct + self.wrong)
			self.recall = float(self.correct) / float(self.correct + self.not_mapped)
			self.fmeasure = (2 * (self.precision * self.recall)) / (self.precision + self.recall)
		except:
			pass

	def diff(self, other):
		result = ReferenceMappingStatistics()

		result.correct = self.correct - other.correct
		result.wrong = self.wrong - other.wrong
		result.not_mapped = self.not_mapped - other.not_mapped
		result.not_found = self.not_found - other.not_found
		result.total = self.total - other.total
		result.reverse = self.reverse - other.reverse
		result.not_found_comparison = self.not_found_comparison - other.not_found_comparison

		try:
			result.maptime = self.maptime - other.maptime
		except:
			pass

		return result


class SAMRow:
	def __init__(self):
		self.qname = False


class SAMFile:
	def __init__(self, filename):
		self.handle = open(filename, "r")
		self.buffer = [SAMRow(), SAMRow()]
		self.current = -1
		self.current_row = self.buffer[0]

	def close(self):
		self.handle.close()

	def hasLast(self):
		return self.getLast().qname != False

	def getLast(self):
		return self.buffer[(self.current - 1) % len(self.buffer)]

	def getCurr(self):
		return self.current_row

	def getHeader(self):
		self.handle.seek(0)
		header = []
		line = self.handle.readline()
		while line != "" and line[:1] == "@":
			header.append(line.strip())
			line = self.handle.readline()

		self.handle.seek(0)
		return header

	def isSorted(self):
		for line in self.getHeader():
			if "SO:queryname" in line:
				return True
		return False

	def next(self):
		while True:
			line = self.handle.readline()
			if line == "":
				return False

			if line[0] == "@":
				continue

			parts = line.strip().split("\t")

			if len(parts) < 11:
				continue
			else:
				break

		self.current = (self.current + 1) % len(self.buffer)
		row = self.buffer[self.current]
		self.current_row = row

		flags = int(parts[1])

		row.qname = parts[0]
		row.flags = flags
		row.rname = parts[2]
		row.pos = int(parts[3])
		row.mapq = int(parts[4])

		row.is_read1 = (flags & 0x40) != 0
		row.is_read2 = (flags & 0x80) != 0
		row.is_secondary = (flags & 0x900) != 0
		row.is_unmapped = (flags & 0x4) != 0
		row.is_reverse = (flags & 0x10) != 0
		row.is_paired = row.is_read1 or row.is_read2

		return True


class ReferenceMappingStatisticsGenerator:
	def __init__(self):
		self.stats = ReferenceMappingStatistics()
		self.testee_filename = ""
		self.comparison_filename = ""
		self.position_threshold = 50
		self.failed_rows_max = 1000
		self.__warnings = []
		self.__errors = []

	def set_testee(self, filename):
		self.testee_filename = filename

	def set_comparison(self, filename):
		self.comparison_filename = filename

	def set_position_threshold(self, t):
		self.position_threshold = t

	def set_rna(self, enable):
		pass

	def warn(self, msg, filename, pos):
		print(msg)
		self.__warnings.append(tuple([msg, filename, pos]))

	def error(self, msg, filename, pos):
		print(msg)
		self.__errors.append(tuple([msg, filename, pos]))

	def get_warnings(self):
		return self.__warnings

	def get_errors(self):
		return self.__errors

	def get_stats(self):
		return self.stats

	def add_failed_row(self, testee, comparison, reason):
		return  # TODO
		if len(self.stats.failed_rows) < self.failed_rows_max:
			self.stats.failed_rows.append((MappingRow(testee), MappingRow(comparison), reason))

	def compute_real(self):
		sam_test = SAMFile(self.testee_filename)

		while sam_test.next():
			self.stats.total += 1

			# if sam_test.getCurr().is_secondary:
			#    self.stats.ignored_testee+=1
			#    continue

			self.doCompareRowsReal(sam_test.getCurr())

		for i in range(254, -1, -1):
			self.stats.mapq_cumulated[i]["correct"] += self.stats.mapq_cumulated[i + 1]["correct"]
			self.stats.mapq_cumulated[i]["wrong"] += self.stats.mapq_cumulated[i + 1]["wrong"]
		self.stats.computeMeasures()

	def compute(self):
		sam_test = SAMFile(self.testee_filename)
		sam_comp = SAMFile(self.comparison_filename)

		dont_advance_test = False
		warned_testee_end = False
		warned_comp_end = False

		while sam_comp.next():
			self.stats.total += 1

			if dont_advance_test:
				dont_advance_test = False
			else:
				if sam_test.next():
					self.stats.total_testee += 1
				else:
					if not warned_testee_end:
						self.warn("Unexpectedly reached end of testee mapping", self.testee_filename,
								  sam_comp.getCurr().qname)
						warned_testee_end = True

					self.stats.not_found += 1
					continue

			# Check if source read identifiers are equal
			# If source read is not equal, theres been a shift in the rows of one of the alignments
			# which we have to adapt for
			while sam_test.getCurr().qname != sam_comp.getCurr().qname or sam_test.getCurr().is_secondary:
				if sam_test.getCurr().is_secondary:
					self.stats.ignored_testee += 1
					self.stats.total_testee += 1

					if not sam_test.next():
						self.warn("Unexpectedly reached end of testee mapped file while skipping secondary alignment",
								  self.testee_filename, sam_comp.getCurr().qname)
						break

					continue

				if sam_test.getCurr().qname > sam_comp.getCurr().qname:
					self.stats.not_found += 1

					if not sam_comp.next():
						self.warn(
							"Unexpectedly reached end of comparison mapped file while looking for alignment with query name",
							self.comparison_filename, sam_test.getCurr().qname)
						break

					self.stats.total += 1
				else:
					self.stats.not_found_comparison += 1
					if not sam_test.next():
						self.warn(
							"Unexpectedly reached end of testee mapped file while looking for alignment with query name",
							self.testee_filename, sam_comp.getCurr().qname)
						break
					self.stats.total_testee += 1

			# Handle paired end reads
			if sam_test.getCurr().is_paired or sam_comp.getCurr().is_paired:
				# Some sanity checks
				if sam_test.getCurr().is_paired and not sam_comp.getCurr().is_paired:
					self.warn("Testee read is part of a pair, but comparison read not", self.testee_filename,
							  sam_test.getCurr().qname)

				if sam_comp.getCurr().is_paired and not sam_test.getCurr().is_paired:
					self.warn("Comparison read is part of a pair, but test read not", self.testee_filename,
							  sam_test.getCurr().qname)

				# Dealing with paired end reads here
				if sam_test.getCurr().is_read1 and sam_comp.getCurr().is_read2:
					if sam_test.getLast() and sam_test.getLast().qname == sam_comp.getCurr().qname and sam_test.getLast().is_read2:
						self.doCompareRows(sam_test.getLast(), sam_comp.getCurr())
						continue
					else:
						if not sam_test.next():
							self.warn("Reached end of testee mapping while looking for pair", self.testee_filename,
									  sam_comp.getCurr().qname)
							break

						dont_advance_test = True

						if sam_test.getCurr().qname == sam_comp.getCurr().qname and sam_test.getCurr().is_read2:
							self.doCompareRows(sam_test.getCurr(), sam_comp.getCurr())
						else:
							self.warn("Could not match pairs", self.testee_filename, sam_test.getCurr().qname)

						continue

				elif sam_test.getCurr().is_read2 and sam_comp.getCurr().is_read1:
					if sam_test.getLast() and sam_test.getLast().qname == sam_comp.getCurr().qname and sam_test.getLast().is_read1:
						self.doCompareRows(sam_test.getLast(), sam_comp.getCurr())
						continue
					else:
						if not sam_test.next():
							self.warn("Reached end of testee mapping while looking for pair", self.testee_filename,
									  sam_comp.getCurr().qname)
							break
						dont_advance_test = True

						if sam_test.getCurr().qname == sam_comp.getCurr().qname and sam_test.getCurr().is_read1:
							self.doCompareRows(sam_test.getCurr(), sam_comp.getCurr())
						else:
							self.warn("Could not match pairs", self.testee_filename, sam_test.getCurr().qname)
						continue

			self.doCompareRows(sam_test.getCurr(), sam_comp.getCurr())

		while sam_test.next():
			self.stats.not_found_comparison += 1
			self.stats.total_testee += 1

			if not warned_comp_end:
				self.warn("Unexpectedly reached end of comparison mapping", self.comparison_filename,
						  sam_test.getCurr().qname)
				warned_comp_end = True

		# Sum up mapping qualities
		correct_sum = 0
		wrong_sum = 0
		for i in range(254, -1, -1):
			self.stats.mapq_cumulated[i]["correct"] += self.stats.mapq_cumulated[i + 1]["correct"]
			self.stats.mapq_cumulated[i]["wrong"] += self.stats.mapq_cumulated[i + 1]["wrong"]

		self.stats.computeMeasures()

	def doCompareRows(self, row_testee, row_comp):
		# Check if was mapped
		if row_testee.is_unmapped:
			self.stats.not_mapped += 1
			self.add_failed_row(row_testee, row_comp, "unmapped")
			return

		if row_testee.rname != row_comp.rname:
			self.stats.wrong += 1
			self.stats.wrong_chromosome += 1
			self.stats.mapq_cumulated[row_testee.mapq]["wrong"] += 1
			self.add_failed_row(row_testee, row_comp, "position")
			return

		if abs(row_testee.pos - row_comp.pos) > self.position_threshold:
			self.stats.wrong += 1
			self.stats.wrong_pos += 1
			self.stats.mapq_cumulated[row_testee.mapq]["wrong"] += 1
			self.add_failed_row(row_testee, row_comp, "position")
			return

		if row_testee.is_reverse != row_comp.is_reverse:
			self.stats.wrong += 1
			self.stats.reverse += 1
			self.stats.mapq_cumulated[row_testee.mapq]["wrong"] += 1
			self.add_failed_row(row_testee, row_comp, "reverse")
			return

		self.stats.mapq_cumulated[row_testee.mapq]["correct"] += 1
		self.stats.correct += 1

	def doCompareRowsReal(self, row_testee):
		# Check if was mapped
		if row_testee.is_unmapped:
			self.stats.not_mapped += 1
		else:
			self.stats.correct += 1
			self.stats.mapq_cumulated[row_testee.mapq]["correct"] += 1


class MappingRow:
	def __init__(self, alignment=None):
		# Disabled, for now
		return

		if alignment == None:
			return

		self.qname = alignment.qname
		self.rname = alignment.rname
		self.pos = alignment.pos
		self.mapq = alignment.mapq
		self.rnext = alignment.rnext
		self.pnext = alignment.pnext
		self.is_duplicate = alignment.is_duplicate
		self.is_paired = alignment.is_paired
		self.is_proper_pair = alignment.is_proper_pair
		self.is_qcfail = alignment.is_qcfail
		self.is_read1 = alignment.is_read1
		self.is_read2 = alignment.is_read2
		self.is_reverse = alignment.is_reverse
		self.is_secondary = alignment.is_secondary
		self.is_unmapped = alignment.is_unmapped
		self.mate_is_reverse = alignment.mate_is_reverse
		self.mate_is_unmapped = alignment.mate_is_unmapped
		self.seq = alignment.seq


if __name__ == "__main__":
	import sys

	if len(sys.argv) < 3:
		print("Usage: stats.py <testee_aligment.sam> <comparison_alignment.sam> <position threshold (default 50)>")
		raise SystemExit

	gen = ReferenceMappingStatisticsGenerator()

	if len(sys.argv) >= 4:
		gen.set_position_threshold(int(sys.argv[3]))

	gen.set_testee(sys.argv[1])
	gen.set_comparison(sys.argv[2])
	gen.compute()
	s = gen.get_stats()
	print(s.to_csv())