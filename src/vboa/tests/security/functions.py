import ast

def set_dict_app_security(path_files):
    """
    Method to obtain a dict with information needed to test the security of the app
    
    :param path_files: str with the path files
    :type path_files: str
    """

    dict_app_security = {
        "authentication_required": [],
        "authentication_not_required": [],
        "roles": {}
    }

    # Iterate through files
    for path_file in iter(path_files.splitlines()):
        source = open(path_file).read()
        
        for node in ast.walk(ast.parse(source)):
            # Check whether the node is a function
            if isinstance(node, ast.FunctionDef):
                # Check whether the function has decorators
                if node.decorator_list:
                    function_decorators = []
                    roles = []
                    route = ""
                    # Iterate through the decorators of the function
                    for decorator in node.decorator_list:
                        # The relevant decorators are a function call (ast.Call)
                        if isinstance(decorator, ast.Call):
                            # For decorator route (ast.Attribute)
                            if isinstance(decorator.func, ast.Attribute):
                                decorator_name = str(decorator.func.attr)
                            # For decorators roles_accepted and auth_required (ast.Name)
                            else: 
                                decorator_name = str(decorator.func.id)
                            # end if

                            # Insert the relevant decorators into the list
                            if decorator_name in ["route", "auth_required", "roles_accepted"]:
                                function_decorators.append(decorator_name)
                            # end if

                            # Check whether the decorator is @roles_accepted type to obtain the roles
                            if decorator_name == "route":
                                route = [str(arg.s) for arg in decorator.args][0]
                            # end if

                            # Check whether the decorator is @roles_accepted type to obtain the roles
                            if decorator_name == "roles_accepted":
                                roles = [str(arg.s) for arg in decorator.args]
                            # end if
                        # end if

                    # end for

                    # Populate the dict based on the decorators of the function
                    if len(function_decorators) > 0:

                        # Check route decorator
                        if not "route" in function_decorators:
                            print("The method '{}' in module '{}' has decorators for security but does not define a route decorator".format(str(node.name), path_file))
                            continue
                        # end if

                        if not function_decorators[0] == "route":
                            print("The method '{}' in module '{}' defines the route decorator '{}' but it is not defined as the first one".format(str(node.name), path_file, route))
                            continue
                        # end if

                        # Check auth_required decorator
                        if not "auth_required" in function_decorators:
                            if "roles_accepted" in function_decorators:
                                print("The method '{}' in module '{}' associated to the route '{}' does not define the auth_required decorator but defines the roles_accepted decorator".format(str(node.name), path_file, route))
                                continue
                            else:
                                dict_app_security["authentication_not_required"].append({
                                    "method_name": node.name,
                                    "module_name": path_file,
                                    "route": route
                                })
                            # end if
                        elif not function_decorators[1] == "auth_required":
                            print("The method '{}' in module '{}' associated to the route '{}' does not define the auth_required decorator after the route decorator".format(str(node.name), path_file, route))
                            continue
                        else:
                            dict_app_security["authentication_required"].append({
                                "method_name": node.name,
                                "module_name": path_file,
                                "route": route
                            })                            
                        # end if

                        # Check roles_accepted decorator
                        if "roles_accepted" in function_decorators:
                            for role in roles:
                                if role not in dict_app_security["roles"]:
                                    dict_app_security["roles"][role] = []
                                # end if
                                dict_app_security["roles"][role].append({
                                    "method_name": node.name,
                                    "module_name": path_file,
                                    "route": route
                                })
                            # end for
                        # end if
                    # end if
                # end if
            # end if
        # end for
    # end for

    return dict_app_security
