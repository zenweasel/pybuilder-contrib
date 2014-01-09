#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a cut and paste of the integration tests plugin. Intended for running Selenium/Behave type
Acceptance tests
"""


import os
import sys

from pybuilder.core import init, use_plugin, task, description, depends
from pybuilder.utils import execute_command, Timer
from pybuilder.terminal import print_text_line, print_file_content
from pybuilder.plugins.python.test_plugin_helper import ReportsProcessor

use_plugin("python.core")


@init
def init_test_source_directory(project):
    project.set_property_if_unset(
        "dir_source_acceptancetest_python", "src/acceptancetests/python")
    project.set_property_if_unset("acceptancetest_file_suffix", "_tests.py")
    project.set_property_if_unset("acceptancetest_additional_environment", {})
    project.set_property_if_unset("acceptancetest_inherit_environment", False)


@task
@description("Runs acceptance tests based on the Behave module")
def run_acceptance_tests(project, logger):
    if not project.get_property("acceptancetest_parallel"):
        reports, total_time = run_acceptance_tests_sequentially(
            project, logger)
    else:
        reports, total_time = run_acceptance_tests_in_parallel(
            project, logger)

    reports_processor = ReportsProcessor(project, logger)
    reports_processor.process_reports(reports, total_time)
    reports_processor.write_report_and_ensure_all_tests_passed()


def run_acceptance_tests_sequentially(project, logger):
    logger.debug("Running acceptance tests sequentially")
    reports_dir = prepare_reports_directory(project)

    report_items = []

    total_time = Timer.start()

    for test in discover_acceptance_tests_for_project(project):
        report_item = run_single_test(logger, project, reports_dir, test)
        report_items.append(report_item)

    total_time.stop()

    return (report_items, total_time)


def run_acceptance_tests_in_parallel(project, logger):
    import multiprocessing
    tests = multiprocessing.Queue()
    reports = multiprocessing.Queue()
    reports_dir = prepare_reports_directory(project)
    cpu_scaling_factor = project.get_property(
        'acceptancetest_cpu_scaling_factor', 4)
    cpu_count = multiprocessing.cpu_count()
    worker_pool_size = cpu_count * cpu_scaling_factor

    logger.debug(
        "Running acceptance tests in parallel with {0} processes ({1} cpus found)".format(
            worker_pool_size,
            cpu_count))

    total_time = Timer.start()
    for test in discover_acceptance_tests_for_project(project):
        tests.put(test)

    def pick_and_run_tests_then_report(tests, reports, reports_dir, logger, project):
        while True:
            try:
                test = tests.get_nowait()
                report_item = run_single_test(
                    logger, project, reports_dir, test)
                reports.put(report_item)
            except:
                break

    pool = []
    for i in range(worker_pool_size):
        p = multiprocessing.Process(
            target=pick_and_run_tests_then_report, args=(tests, reports, reports_dir, logger, project))
        pool.append(p)
        p.start()

    for worker in pool:
        worker.join()

    total_time.stop()

    iterable_reports = []
    while True:
        try:
            iterable_reports.append(reports.get_nowait())
        except:
            break

    return (iterable_reports, total_time)


def discover_acceptance_tests(source_path, suffix=".py"):
    result = []
    for root, _, files in os.walk(source_path):
        for file_name in files:
            if file_name.endswith(suffix):
                result.append(os.path.join(root, file_name))
    return result


def discover_acceptance_tests_for_project(project):
    acceptancetest_source_dir = project.expand_path(
        "$dir_source_acceptancetest_python")
    acceptancetest_suffix = project.expand("$acceptancetest_file_suffix")
    return discover_acceptance_tests(acceptancetest_source_dir, acceptancetest_suffix)


def add_additional_environment_keys(env, project):
    additional_environment = project.get_property(
        "acceptancetest_additional_environment", {})
    # TODO: assert that additional env is a map
    for key in additional_environment:
        env[key] = additional_environment[key]


def inherit_environment(env, project):
    if project.get_property("acceptancetest_inherit_environment", False):
        for key in os.environ:
            if key not in env:
                env[key] = os.environ[key]


def prepare_environment(project):
    env = {
        "PYTHONPATH": os.pathsep.join((project.expand_path("$dir_dist"),
                                       project.expand_path("$dir_source_acceptancetest_python")))
    }

    inherit_environment(env, project)

    add_additional_environment_keys(env, project)

    return env


def prepare_reports_directory(project):
    reports_dir = project.expand_path("$dir_reports/acceptancetests")
    if not os.path.exists(reports_dir):
        os.mkdir(reports_dir)
    return reports_dir


def run_single_test(logger, project, reports_dir, test, ):
    name, _ = os.path.splitext(os.path.basename(test))
    logger.info("Running acceptance test %s", name)
    env = prepare_environment(project)
    test_time = Timer.start()
    command_and_arguments = (sys.executable, test)
    report_file_name = os.path.join(reports_dir, name)
    error_file_name = report_file_name + ".err"
    return_code = execute_command(
        command_and_arguments, report_file_name, env, error_file_name=error_file_name)
    test_time.stop()
    report_item = {
        "test": name,
        "test_file": test,
        "time": test_time.get_millis(),
        "success": True
    }
    if return_code != 0:
        logger.error("acceptance test failed: %s", test)
        report_item["success"] = False

        if project.get_property("verbose"):
            print_file_content(report_file_name)
            print_text_line()
            print_file_content(error_file_name)

    return report_item
@init
def init_my_plugin(project):
    project.build_depends_on("splinter")

@task
@depends("prepare")
@description("a task that complies with the verbose flag")
def my_verbose_compliant_task(project, logger):
    # is true if user set verbose in build.py or from command line
    verbose_flag = project.get_property("verbose")
    project.set_property("my_plugin_verbose_output", verbose_flag)

    # verbose output if "my_plugin_verbose_output" is True
    execute_tool_on_source_files(project=project,
                                 name="my_plugin",
                                 command_and_arguments=["/usr/bin/file",
                                                        "-bi"],
                                 logger=logger)