import time
import os
import sys
import math

import yaml

from report_page import Page
from lib import util

strftime = time.strftime


class ReportHTMLGenerator:
	def __init__(self, mate, plotgen):
		self.mate = mate
		self.collapse_counter = 0
		self.tabpane_counter = 0
		self.plotgen = plotgen

	def nltobr(self, text):
		if text == None:
			return None
		else:
			return text.replace('\n', '<br>\n')

	def write(self, text):
		self.html += text

	def openPanel(self, title="Panel", style="default"):
		return '<div class="panel panel-' + style + '"><div class="panel-heading"><h1 class="panel-title">' + title + '</h1></div><div class="panel-body">'

	def closePanel(self):
		return "</div></div>"

	def collapsible(self, heading, text, opened=False):
		return self.openCollapsiblePanel(heading, opened) + text + self.closeCollapsiblePanel()

	def openCollapsiblePanel(self, heading, opened=False):
		self.collapse_counter = self.collapse_counter + 1
		the_id = str(self.collapse_counter)

		if not opened:
			return '<div class="panel panel-default" id="panel1"><div class="panel-heading"><h4 class="panel-title"><a href="javascript:void(0);" data-toggle="collapse" data-target="#collapse' + the_id + '" class=\"collapsed\">' + heading + '</a></h4></div><div id="collapse' + the_id + '" class="panel-collapse collapse"><div class="panel-body">'
		else:
			return '<div class="panel panel-default" id="panel1"><div class="panel-heading"><h4 class="panel-title"><a href="javascript:void(0);" data-toggle="collapse" data-target="#collapse' + the_id + '">' + heading + '</a></h4></div><div id="collapse' + the_id + '" class="panel-collapse collapse-in"><div class="panel-body">'

	def closeCollapsiblePanel(self):
		return '</div></div></div>'

	def getMapperBinaryPath(self, mapper):
		return str(self.mate._("mappers:" + mapper + ":bin"))

	def makeTestNavList(self):
		list = []
		for test_name in sorted(self.mate.getTestNameList()):
			test_objects = self.mate.getTestsByName(test_name)
			if len(test_objects) == 0:
				continue

			test = test_objects[0]
			list.append({"title": test.getTitle(), "link": test.getName() + ".html"})
		return list

	def makeTestMapperNavList(self, test_objects):
		list = []
		for test in test_objects:
			list.append({"title": test.getMapper().getTitle(), "link": test.getFullName() + ".html"})
		return list

	def generateMainErrorList(self):
		if len(self.mate.getWarnings()) + len(self.mate.getErrors()) == 0:
			return ""

		html = ""

		html += "<table class=\"table table-striped\">"
		html += "<thead>"
		html += "<tr>"
		html += "<th>Type</th>"
		html += "<th>Message</th>"
		html += "</tr>"
		html += "</thead>"
		html += "<tbody>"

		for msg in self.mate.getWarnings():
			html += "<tr>"
			html += "<td class=\"col-md-1 warning\" align=\"center\"><span class=\"glyphicon glyphicon-exclamation-sign\"></span></td>"
			html += "<td>" + str(msg) + "</td>"
			html += "</tr>"

		for msg in self.mate.getErrors():
			html += "<tr>"
			html += "<td class=\"col-md-1 danger\" align=\"center\"><span class=\"glyphicon glyphicon-remove\"></span></td>"
			html += "<td>" + str(msg) + "</td>"
			html += "</tr>"

		html += "</table>"

		return html

	def generateErrorList(self, test):
		html = ""

		if len(test.getWarnings()) + len(test.getErrors()) == 0:
			html = "<i>No problems were encountered.</i>"
			return html

		html += "<table class=\"table table-striped\">"
		html += "<thead>"
		html += "<tr>"
		html += "<th>Type</th>"
		html += "<th>Message</th>"
		html += "<th>File</th>"
		html += "<th>Position</th>"
		html += "</tr>"
		html += "</thead>"
		html += "<tbody>"

		for msg, file, location in test.getWarnings():
			html += "<tr>"
			html += "<td class=\"col-md-1 warning\" align=\"center\"><span class=\"glyphicon glyphicon-exclamation-sign\"></span></td>"
			html += "<td>" + str(msg) + "</td>"
			html += "<td>" + str(file) + "</td>"
			html += "<td>" + str(location) + "</td>"
			html += "</tr>"

		for msg, file, location in test.getErrors():
			html += "<tr>"
			html += "<td class=\"col-md-1 danger\" align=\"center\"><span class=\"glyphicon glyphicon-remove\"></span></td>"
			html += "<td>" + str(msg) + "</td>"
			html += "<td>" + str(file) + "</td>"
			html += "<td>" + str(location) + "</td>"
			html += "</tr>"

		html += "</table>"

		return html

	def generateOverviewErrorList(self, test_objects):
		html = ""

		html += "<table class=\"table table-striped\">"
		html += "<thead>"
		html += "<tr>"
		html += "<th>Source</th>"
		html += "<th>Message</th>"
		html += "<th>File</th>"
		html += "<th>Position</th>"
		html += "</tr>"
		html += "</thead>"
		html += "<tbody>"

		for msg, file, location in self.mate.getErrors():
			html += "<tr>"
			html += "<td class=\"col-md-1 danger\">Teaser</td>"
			html += "<td>" + str(msg) + "</td>"
			html += "<td>" + str(file) + "</td>"
			html += "<td>" + str(location) + "</td>"
			html += "</tr>"

		for test in test_objects:
			for msg, file, location in test.getErrors():
				html += "<tr>"
				html += "<td class=\"col-md-1 danger\">" + test.getMapper().getTitle() + "</td>"
				html += "<td>" + str(msg) + "</td>"
				html += "<td>" + str(file) + "</td>"
				html += "<td>" + str(location) + "</td>"
				html += "</tr>"

		html += "</table>"

		return html

	def generateMainErrorList(self):
		html = ""

		if len(self.mate.getWarnings()) + len(self.mate.getWarnings()) == 0:
			html = "<i>No problems were encountered.</i>"
			return html

		html += "<table class=\"table table-striped\">"
		html += "<thead>"
		html += "<tr>"
		html += "<th>Type</th>"
		html += "<th>Message</th>"
		html += "</tr>"
		html += "</thead>"
		html += "<tbody>"

		for msg in self.mate.getWarnings():
			html += "<tr>"
			html += "<td class=\"col-md-1 warning\" align=\"center\"><span class=\"glyphicon glyphicon-exclamation-sign\"></span></td>"
			html += "<td>" + str(msg) + "</td>"
			html += "</tr>"

		for msg in self.mate.getErrors():
			html += "<tr>"
			html += "<td class=\"col-md-1 danger\" align=\"center\"><span class=\"glyphicon glyphicon-remove\"></span></td>"
			html += "<td>" + str(msg) + "</td>"
			html += "</tr>"

		html += "</table>"

		return html

	def generateTestList(self):
		html = ""

		html += str(self.mate.tests_run_count) + " tests executed, " + str(
			self.mate.tests_run_count - self.mate.tests_success_count) + " fail, " + str(
			self.mate.tests_aborted_count) + " aborted, " + str(self.mate.tests_err_count) + " errors total."
		html += "<table class=\"table table-striped\">"
		html += "<thead>"
		html += "<tr>"
		html += "<th>State</th>"
		html += "<th>Name</th>"
		html += "<th>Executed</th>"
		html += "<th>OK</th>"
		html += "<th>Warnings</th>"
		html += "<th>Errors</th>"
		html += "<th>Runtime</th>"
		html += "</tr>"
		html += "</thead>"

		for test_name in sorted(self.mate.getTestNameList()):
			tests = self.mate.getTestsByName(test_name)
			if len(tests) == 0:
				continue

			success = 0
			total = 0
			warnings = 0
			errors = 0
			time = 0

			show_test = True
			for test in tests:

				if self.mate.run_only != False and not test.getName() in self.mate.run_only:
					show_test = False
					break

				# if not test.getWasRun() or not self.mate.isTestIncluded(test):
				#	show_test = False
				#	break

				total += 1
				if test.getSuccess():
					success += 1

				warnings += test.getWarningCount()
				errors += test.getErrorCount()
				time += test.getRunTime()

			test = tests[0]

			if not show_test:
				continue

			tclass = "info"
			icon = "glyphicon-ok"

			if warnings > 0:
				tclass = "warning"
				icon = "glyphicon-exclamation-sign"

			if success != total:
				tclass = "danger"
				icon = "glyphicon-remove"

			html += "<tr>"
			html += "<td class=\"col-md-1 " + tclass + "\" align=\"center\"><span class=\"glyphicon " + icon + "\"></span></td>"
			html += "<td><a href=\"" + test.getName() + ".html\">" + test.getTitle() + "</a></td>"
			html += "<td>%d</td>" % total
			html += "<td>%d</td>" % success
			html += "<td>%d</td>" % warnings
			html += "<td>%d</td>" % errors
			html += "<td>%ds (%ds gen + %ds run)</td>" % (time + test.getCreateTime(), test.getCreateTime(), time)
			html += "</tr>"

		html += "</table>"
		return html

	def generateSetup(self):
		html = ""
		html += "<table class=\"table table-striped\" style=\"margin-bottom;5px;\">"
		html += "<tbody>"
		html += "<tr>"
		html += "<th class=\"col-md-2\">Teaser Accession</th>"
		html += "<td class=\"col-md-8\">" + self.mate._("report:name") + "</td>"
		html += "</tr>"
		html += "<tr>"
		html += "<th>Report timestamp</th>"
		html += "<td>" + time.ctime() + "</td>"
		html += "</tr>"
		html += "<tr>"
		html += "<tr>"
		html += "<th>Framework Version</th>"
		html += "<td>" + self.mate.version() + "-" + self.mate.getCondensedVersionHash() + "</td>"
		html += "</tr>"
		html += "<th>Framework Working Directory</th>"
		html += "<td>" + os.getcwd() + "</td>"
		html += "</tr>"
		html += "<tr>"
		html += "<th>Framework Command Line</th>"
		html += "<td>" + " ".join(sys.argv) + "</td>"
		html += "</tr>"
		html += "<tr>"
		html += "<th>Wall Clock Time (Framework)</th>"
		html += "<td>%ds</td>" % self.mate.getWallClockTime()
		html += "</tr>"
		html += "<tr>"
		html += "<th>Wall Clock Time (Mappers)</th>"
		html += "<td>%ds</td>" % self.mate.getMapperWallClockTime()
		html += "</tr>"
		html += "<tr>"
		html += "<th colspan=\"2\">Benchmark Configuration</th>"
		html += "</tr>"
		html += "<tr>"
		html += "<td colspan=\"2\"><pre>" + yaml.dump(self.mate.config_original) + "</pre></td>"
		html += "</tr>"
		html += "</tbody>"
		html += "</table>"

		return html

	def generateLogs(self):
		html = ""
		html += "<pre>" + self.mate.getLogFileContents() + "</pre>"
		return html

	def generateSubprocessOutputs(self, test):
		subprocess_text = ""
		for sub, desc in test.getSubResults():
			if sub["command"].strip() == "":
				continue

			subprocess_text += self.openPanel(sub["command"])
			subprocess_text += "<table class=\"table table-striped\" style=\"margin-bottom;5px;\">"
			subprocess_text += "<tbody>"

			for key in sorted(sub):
				text = str(sub[key]).replace('\n', '<br>\n')
				if key == "stdout" or key == "stderr":
					text = self.collapsible(key, "<pre>" + text + "</pre>")

				subprocess_text += "<tr>"
				subprocess_text += "<th class=\"col-md-2\">" + str(key) + "</th>"
				subprocess_text += "<td class=\"col-md-8\"><small>" + text + "</small></td>"
				subprocess_text += "</tr>"

			subprocess_text += "</tbody>"
			subprocess_text += "</table>"
			subprocess_text += self.closePanel()

		return subprocess_text

	def generateOverviewPlot(self, page, measure):
		format_func = "function(y){return y;}"
		min = 0
		if measure == "correct":
			title = "Correct reads"
			format_func = "function(y){return Math.round(100000*y)/100000 + \"%\";}"
		elif measure == "corrects":
			title = "Correct/s"
			format_func = "function(y){return Math.round(1000*y)/1000;}"
		elif measure == "precision":
			title = "Precision"
			format_func = "function(y){return Math.round(10000*y)/10000;}"
			# min = 0.75
		elif measure == "recall":
			title = "Recall"
			format_func = "function(y){return Math.round(10000*y)/10000;}"
			# min = 0.75
		elif measure == "fmeasure":
			title = "F-Measure"
			format_func = "function(y){return Math.round(10000*y)/10000;}"
			# min = 0.75

		import json

		data = []
		for mapper in sorted(self.mate.getMappers()):
			column = []
			for test_name in self.mate.getTestNameList():
				test = self.mate.getTestByMapperName(test_name, mapper)
				if len(column) == 0:
					column.append(test.getMapper().getTitle())

				if test.getRunResults() == None:
					column.append(0)
					continue

				if measure == "correct":
					value = test.getRunResults().correct / float(test.getRunResults().total)
					value = value * 100
				elif measure == "corrects":

					try:
						value = test.getRunResults().correct / float(test.getRunResults().maptime)
					except ZeroDivisionError:
						value = 0

						# TODO
						# if value < 1:
						#    value = 1

						# value = math.log(value, 10)
				elif measure == "precision":
					value = test.getRunResults().precision
				elif measure == "recall":
					value = test.getRunResults().recall
				elif measure == "fmeasure":
					value = test.getRunResults().fmeasure
				value = round(value, 4)
				column.append(value)
			data.append(column)

		if min != 0:
			min_str = ",min: %f" % min
		else:
			min_str = ""

		titles = []
		for name in self.mate.getTestNameList():
			tests = self.mate.getTestsByName(name)
			if len(tests) != 0:
				titles.append(tests[0].getTitle())
		# titles=["0%","75%","90%","95%","99%"]
		page.addSection("Results: %s" % title, """<div id="plot_%s"></div>""" % measure)
		page.addScript("""
var chart_%s = c3.generate({
    bindto: '#plot_%s',
    size: {
      height: 400
    },
    data: {
      columns: %s
    },
    grid: {
      y: {
        show: true
      }
    },
    axis: {
      x: {
        type: "category",
        categories: %s,
        label:
        {
              text: "Data Set"//,
              //position: "outer-center"
        }
      },

      y: {
        label:
        {
              text: "%s",
              position: "outer-middle"
        },
        tick: { format: %s }
        %s
      }
    },
    legend: {
    	position: "right",
    	show:true
    },
    padding: {
        bottom: 60
    }

});""" % (measure, measure, json.dumps(data), json.dumps(titles), title, format_func, min_str))

	def generate(self):
		if self.mate.publicate_export:
			self.mate.pushLogPrefix("PublicateExp")
			self.mate.log("Init")

			import report_plot

			pgen = report_plot.ReportPlotGenerator(self.mate)

			self.mate.log("Generate: Mapping Overview Plot: Correct")
			# pgen.generateSamplingMappingOverviewPlot("correct")
			# pgen.generateRuntimeReductionPlot()
			# pgen.generateMappingOverviewPlot("correct")
			# pgen.generateMappingOverviewPlotCorrectPerSec()
			# pgen.generateMappingOverviewBarPlot("correct")
			# pgen.generateMappingOverviewBarPlot("corrects")

			for test_name in sorted(self.mate.getTestNameList()):
				pgen.generateMappingScatterPlotFor(test_name)

			self.mate.popLogPrefix()

		self.mate.pushLogPrefix("ReportGen")

		number_of_tests=sum([1 if len(self.mate.getTestsByName(name)) else 0 for name in self.mate.getTestNameList()])
		if number_of_tests == 0:
			self.mate.warning("This benchmark contains no tests. Were any mappers selected for testing?")

		index = Page()

		index.addSection("Tests Overview", self.generateTestList())
		index.addNav([{"title": "Benchmark", "link": "start.html"}])
		index.addNav(self.makeTestNavList(), "Select Test")

		index.addSection("Errors and Warnings", self.generateMainErrorList())

		self.generateOverviewPlot(index, "correct")
		self.generateOverviewPlot(index, "corrects")
		self.generateOverviewPlot(index, "precision")
		self.generateOverviewPlot(index, "recall")
		self.generateOverviewPlot(index, "fmeasure")

		csv = "test,mapper,correct_percent,time_gen,time_run,time_map\n"
		for test_name in self.mate.getTestNameList():
			for test in self.mate.getTestsByName(test_name):
				csv += "%s,%s,%f,%f,%f,%f\n" % (
				test_name, test.getMapper().getName() + " " + test.getMapper().param_string.replace(",", ";"),
				(100.0 * test.getRunResults().correct) / float(test.getRunResults().total), test.getCreateTime(),
				test.getRunTime(), test.getRunResults().total / float(test.getRunResults().maptime))

		index.addSection("Raw Results", "<pre>%s</pre>" % csv)

		index.addSection("Setup", self.generateSetup())
		index.addSection("Log", self.generateLogs())

		with open(self.mate.getReportDirectory() + "/start.html", "w") as handle:
			handle.write(index.html())

		if number_of_tests != 1:
			with open(self.mate.getReportDirectory() + "/index.html", "w") as handle:
				handle.write(index.html())

		for test_name in sorted(self.mate.getTestNameList()):
			test_objects = self.mate.getTestsByName(test_name)
			if len(test_objects) == 0:
				continue
			test = test_objects[0]

			test_page = Page()
			test_page.addNav([{"title": "Benchmark", "link": "start.html"}])
			test_page.addNav(self.makeTestNavList(), test.getTitle())
			test_page.addNav(self.makeTestMapperNavList(test_objects), "Select Mapper")

			if len(self.mate.getErrors()) + sum([len(test.getErrors()) for test in test_objects]) > 0:
				test_page.addSection("Errors and Warnings", self.generateOverviewErrorList())

			test.executePipeline("report_overview", [self, test_page, test_objects])
			with open(self.mate.getReportDirectory() + "/" + test.getName() + ".html", "w") as handle:
				handle.write(test_page.html())

			if number_of_tests == 1:
				with open(self.mate.getReportDirectory() + "/index.html", "w") as handle:
					handle.write(test_page.html())

			for test in test_objects:
				test_mapper_page = Page()
				test_mapper_page.addNav([{"title": "Benchmark", "link": "start.html"}])
				test_mapper_page.addNav(self.makeTestNavList(), test.getTitle())
				test_mapper_page.addNav(self.makeTestMapperNavList(test_objects), test.getMapper().getTitle())

				test.executePipeline("report_detail", [self, test_mapper_page])

				test_mapper_page.addSection("Errors and Warnings", self.generateErrorList(test))
				test_mapper_page.addSection("Subprocess Log", self.generateSubprocessOutputs(test))

				with open(self.mate.getReportDirectory() + "/" + test.getFullName() + ".html", "w") as handle:
					handle.write(test_mapper_page.html())


		self.mate.popLogPrefix()

	def generateProgress(self):
		total_to_run = self.mate.getTestsToRunCount() + 1
		total_ran = self.mate.getTestsRanCount() + 1
		progress_text = ""
		if self.mate.getTeaser() != None:
			total_to_run += self.mate.getTeaser().getTestCount()
			total_ran += self.mate.getTeaser().getTestCreatedCount()
			if self.mate.getTeaser().getTestCreatedCount() < self.mate.getTeaser().getTestCount():
				progress_text = "Create simulated data set %d of %d..." % (
					self.mate.getTeaser().getTestCreatedCount() + 1, self.mate.getTeaser().getTestCount())
				# Hack!
				total_to_run += len(self.mate.config["test_mappers"]) * self.mate.getTeaser().getTestCount()
		try:
			progress_percent = 100 * (float(total_ran) / float(total_to_run))
		except ZeroDivisionError:
			progress_percent = 0

		if progress_percent == 100:
			progress_percent=0
			progress_text="Preparing..."

		if progress_text == "":
			if self.mate.getCurrentTest() != None:
				progress_text = "Test %s for data set %s..." % (
					self.mate.getCurrentTest().getMapper().getTitle(), self.mate.getCurrentTest().getTitle())

		index = Page()
		index.addNav([{"title": "Benchmark", "link": "index.html"}])
		index.addSection("Teaser is running...", """<META HTTP-EQUIV="refresh" CONTENT="3"> Job submitted %dm ago. Benchmark results will show on this page after completion. <a href="index.html">Click here if this page does not refresh.</a> <div class="progress" style="margin-top:15px; margin-bottom: 1px;">
  <div class="progress-bar progress-bar-info progress-bar-striped active" role="progressbar" aria-valuenow="%d"
  aria-valuemin="0" aria-valuemax="100" style="width:%d%%; height:30px;">
	 %d%%
  </div>
</div>
<small>%s</small>""" % (
			int(self.mate.getElapsedTime()/60), progress_percent, progress_percent, progress_percent, progress_text))
		index.addSection("Errors and Warnings", self.generateMainErrorList())
		index.addSection("Setup", self.generateSetup())
		index.addSection("Log", self.generateLogs())

		handle = open(self.mate.getReportDirectory() + "/index.html", "w")
		handle.write(index.html())
		handle.close()
