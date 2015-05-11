import json

from qds_sdk.qubole import Qubole
from qds_sdk.resource import Resource
from argparse import ArgumentParser
from qds_sdk.commands import *
from qds_sdk.actions import *
import argparse

class CommandTemplateCmdLine:
    hiveparser = None
    prestoparser = None
    list_allparser = None
    viewparser = None
    removeparser = None
    runparser = None
    run_and_waitparser = None
    @staticmethod
    def parsers():
        argparser = ArgumentParser(prog="qds.py commandtemplates",
                                        description="Command Templates client for Qubole Data Service.")
        subparsers = argparser.add_subparsers()

        #Hive Command
        hivecmd = subparsers.add_parser("hivecmd", help="Create a new hive command template")
        
        hivecmd.add_argument("--name", dest="name", help="Hive query name", required=True)

        hivecmd.add_argument("--input_vars",
            help="Add names and values for input variables", dest="input_vars", nargs="*")

        hivecmdgroup = hivecmd.add_mutually_exclusive_group(required=True)

        hivecmdgroup.add_argument("--query", dest="query", help="Hive query")

        hivecmdgroup.add_argument("--script_location", dest="script_location", help="S3 path of script")


        hivecmd.add_argument("--macros", dest="macros", help="Hive macros")

        hivecmd.set_defaults(func=CommandTemplateCmdLine.hivecmd)
        
        CommandTemplateCmdLine.hiveparser = hivecmd

        #Presto Command
        prestocmd = subparsers.add_parser("prestocmd", help="Create a new presto command template")

        prestocmd.add_argument("--input_vars",
            help="Add names and values for input variables", dest="input_vars", nargs="*")

        prestocmdgroup = prestocmd.add_mutually_exclusive_group(required=True)

        prestocmdgroup.add_argument("--query", dest="query", help="Presto query")

        prestocmdgroup.add_argument("--script_location", dest="script_location", help="S3 path of script")

        prestocmd.add_argument("--name", dest = "name", help="Presto query name", required = True)

        prestocmd.add_argument("--macros", dest = "macros", help="Presto macros")

        prestocmd.set_defaults(func=CommandTemplateCmdLine.prestocmd)
        
        CommandTemplateCmdLine.prestoparser = prestocmd

        #list_all command
        list_all = subparsers.add_parser("list", help="List all available command templates")

        list_all.add_argument("--fields", nargs="*", dest="fields",
                          help="List of fields to show")
        list_all.add_argument("--per-page", dest="per_page", type=int, 
                          help="Number of items per page")
        list_all.add_argument("--page", dest="page", type=int,
                          help="Page Number")

        list_all.set_defaults(func=CommandTemplateCmdLine.list_all)
        CommandTemplateCmdLine.list_allparser = list_all

        #view command
        view = subparsers.add_parser("view",
                                     help="View a specific command template")
        view.add_argument("--id", help="Numeric id of the command template", dest="id", type=int)
        view.add_argument("--name", help="Name of the command template", dest="name")
        view.add_argument("--fields", nargs="*", dest="fields",
                          help="List of fields to show")
        view.set_defaults(func=CommandTemplateCmdLine.view)
        CommandTemplateCmdLine.viewparser = view

        #remove command
        remove = subparsers.add_parser("remove",
                                     help="Remove a specific command template")
        remove.add_argument("id", help="Numeric id of the command template", type=int)
        remove.set_defaults(func=CommandTemplateCmdLine.remove)
        CommandTemplateCmdLine.removeparser = remove
        CommandTemplateCmdLine.removeparser = remove

        #run command
        run = subparsers.add_parser("run", help="Run a command template")
        run.add_argument("id", help="Numeric id of the command template")
        run.add_argument("--input_vars",
            help="Add names and values for input variables", dest="input_vars", nargs="*")
        run.set_defaults(func=CommandTemplateCmdLine.run_template)
        CommandTemplateCmdLine.runparser = run

        #run_and_wait command
        run_and_wait = subparsers.add_parser("run_and_wait", 
            help="Run a command template and wait for it to complete")

        run_and_wait.add_argument("id", help="Numeric id of the command template")
        run_and_wait.add_argument("--input_vars", 
            help="Add name and values of input variables", dest="input_vars", nargs="*")

        run_and_wait.set_defaults(func=CommandTemplateCmdLine.run_and_wait)
        CommandTemplateCmdLine.run_and_waitparser = run_and_wait
        return argparser

    @staticmethod
    def get_hivecmd_help():
        return CommandTemplateCmdLine.hiveparser.format_help()

    @staticmethod
    def get_prestocmd_help():
        return CommandTemplateCmdLine.prestoparser.format_help()

    @staticmethod
    def get_list_all_help():
        return CommandTemplateCmdLine.list_allparser.format_help()

    @staticmethod
    def get_view_help():
        return CommandTemplateCmdLine.viewparser.format_help()

    @staticmethod
    def get_remove_help():
        return CommandTemplateCmdLine.removeparser.format_help()

    @staticmethod
    def get_run_help():
        return CommandTemplateCmdLine.runparser.format_help()

    @staticmethod
    def get_run_and_wait_help():
        return CommandTemplateCmdLine.run_and_waitparser.format_help()

    @staticmethod
    def run(args):
        parser = CommandTemplateCmdLine.parsers()
        parsed = parser.parse_args(args)
        return parsed.func(parsed)

    @staticmethod
    def filter_fields(schedule, fields):
        filtered = {}
        try:
            for field in fields:
                filtered[field] = schedule[field]
        except KeyError, e:
            raise ParseError("Incorrect field name ",CommandTemplateCmdLine.get_list_all_help() )
        return filtered

    @staticmethod
    def hivecmd(args):
        result_json = CommandTemplate.hivecmd(args)
        return json.dumps(result_json, sort_keys=True, indent=4)

    @staticmethod
    def prestocmd(args):
        result_json = CommandTemplate.prestocmd(args)
        return json.dumps(result_json, sort_keys=True, indent=4)

    @staticmethod
    def list_all(args):
        commandtemplateslist = CommandTemplate.list_all(args)
        if args.fields:
            for s in commandtemplateslist:
                s.attributes = CommandTemplateCmdLine.filter_fields(s.attributes, args.fields)
        return json.dumps(commandtemplateslist, default=lambda o: o.attributes, sort_keys=True, indent=4)

    @staticmethod
    def view(args):
        if args.id:
            commandtemplate = CommandTemplate.find(args.id)
        elif args.name:
            commandtemplate = CommandTemplate.find_by_name(args.name)
        else:
            raise ParseError("Either template id or template name must be specified",CommandTemplateCmdLine.get_view_help() ) 
        if args.fields:
            commandtemplate.attributes = CommandTemplateCmdLine.filter_fields(schedule.attributes, args.fields)
        return json.dumps(commandtemplate.attributes, sort_keys=True, indent=4)

    @staticmethod
    def remove(args):
        commandtemplate = CommandTemplate.find(args.id)
        return json.dumps(commandtemplate.remove(), sort_keys=True, indent=4)

    @staticmethod
    def run_template(args):
        commandtemplate = CommandTemplate.find(args.id)
        return json.dumps(commandtemplate.run_template(args), sort_keys=True, indent=4)

    @staticmethod
    def run_and_wait(args):
        commandtemplate = CommandTemplate.find(args.id)
        cmd = Command.find(commandtemplate.run_template(args)['id'])
        while not Command.is_done(cmd.status):
            time.sleep(Qubole.poll_interval)
            cmd = Command.find(cmd.id)

        if Command.is_success(cmd.status):
            log.info("Fetching results for %s, Id: %s" % (cmdclass.__name__, cmd.id))
            return cmd.get_results(sys.stdout, delim='\t')
        else:
            return "Cannot fetch results - command Id: %s failed with status: %s" % (cmd.id, cmd.status)


class CommandTemplate(Resource):

    rest_entity_path = "command_templates"
    
     
    @staticmethod
    def hivecmd(args):
        conn = Qubole.agent()
        url_path = CommandTemplate.rest_entity_path
        data = {}
        if args.name is not None:
            data['name'] = args.name
        if args.macros is not None:
            data['macros'] = json.loads(args.macros)
        if args.input_vars is not None:
            data['input_vars'] = []
            for input_var in args.input_vars:
                a = input_var.split("=")
                input_var_data = {}
                input_var_data['name'] = a[0]
                if (len(a)>1):
                    input_var_data['default_value'] = a[1]
                data['input_vars'].append(input_var_data)
        data['command'] = {}
        
        hivecmd_help = CommandTemplateCmdLine.get_hivecmd_help()
        if args.script_location is not None:
            if ((args.script_location.find("s3://") != 0) and
                (args.script_location.find("s3n://") != 0)):

                # script location is local file

                try:
                    q = open(args.script_location).read()
                except IOError as e:
                    raise ParseError("Unable to open script location: %s" %
                                     str(e),
                                     hivecmd_help)
                data['command']['query'] = q
            else:
                data['command']['script_location'] = args.script_location
    
        if args.query is not None:
            data['command']['query'] = args.query
        data['command']['command_type'] = "HiveCommand"
        data['command_type'] = "HiveCommand"

        result_json = conn.post(CommandTemplate.rest_entity_path, data=data)

        return result_json

    @staticmethod
    def prestocmd(args):
        conn = Qubole.agent()
        url_path = CommandTemplate.rest_entity_path
        data = {}
        if args.name is not None:
            data['name'] = args.name
        if args.macros is not None:
            data['macros'] = json.loads(args.macros)
        if args.input_vars is not None:
            data['input_vars'] = []
            for input_var in args.input_vars:
                a = input_var.split("=")
                input_var_data = {}
                input_var_data['name'] = a[0]
                if (len(a)>1):
                    input_var_data['default_value'] = a[1]
                data['input_vars'].append(input_var_data)
        data['command'] = {}
        
        prestocmd_help = CommandTemplateCmdLine.get_prestocmd_help()
        
        if args.script_location is not None:
            if ((args.script_location.find("s3://") != 0) and
                (args.script_location.find("s3n://") != 0)):

                # script location is local file

                try:
                    q = open(args.script_location).read()
                except IOError as e:
                    raise ParseError("Unable to open script location: %s" %
                                     str(e),
                                     prestocmd_help)
                data['command']['query'] = q
            else:
                data['command']['script_location'] = args.script_location
    
        if args.query is not None:
            data['command']['query'] = args.query
        
        data['command']['command_type'] = "PrestoCommand"
        data['command_type'] = "PrestoCommand"

        result_json = conn.post(CommandTemplate.rest_entity_path, data=data)

        return result_json

    @staticmethod
    def list_all(args):
        conn = Qubole.agent()
        url_path = CommandTemplate.rest_entity_path
        page_attr = []
        if args.page is not None:
            page_attr.append("page=%s" % args.page)
        if args.per_page is not None:
            page_attr.append("per_page=%s" % args.per_page)
        if page_attr:
            url_path = "%s?%s" % (CommandTemplate.rest_entity_path, "&".join(page_attr))

        myjson = conn.get(url_path)
        commandtemplateslist = []
        for commandtemplate in myjson['command_templates']:
            commandtemplateslist.append(CommandTemplate(commandtemplate))
        return commandtemplateslist

    @staticmethod
    def find_by_name(name):
        conn = Qubole.agent()
        if name is not None:
            #s = "%s?template_name=%s" % (CommandTemplate.rest_entity_path, str(name))
            result_json = (conn.get(CommandTemplate.rest_entity_path, params={"template_name":name}))
            #result_json = (conn.get(s))
            #print result_json["command_templates"][0]
            if result_json["command_templates"]:
                return CommandTemplate(result_json["command_templates"][0])
        return None

    def remove(self):
        conn = Qubole.agent()
        remove_url = "%s/remove" % self.element_path(self.id)
        data = {}
        return conn.put(remove_url, data)

    def run_template(self, args):
        conn = Qubole.agent()
        run_url = "%s/run" % self.element_path(self.id)
        data = {}
        if args.input_vars is not None:
            data['input_vars'] = []
            for input_var in args.input_vars:
                a = input_var.split("=")
                input_var_data = {a[0]:a[1]}
                data['input_vars'].append(input_var_data)
        return conn.post(run_url, data)
