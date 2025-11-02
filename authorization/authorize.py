from django.shortcuts import redirect
from .models import ContextManager, ContextLookup, ContextPosition

AUTH_DECISION = {
    'ALLOW' : 1,
    'DENY' : 0,
    'DO_NOT_CARE' : 2,
    'NO_ROLE' : 3,
}

AUTH_TRACE = "__auth_trace_graph__"

class Authorization:
    #Low level authorization
    def _auth_get_context_decision_(context, pos):
        BLOCK_SIZE = 4
        actualPos = pos // BLOCK_SIZE
        offsetPos = pos % BLOCK_SIZE
        if actualPos >= len(context):
            raise Exception("Unsupported position in the context")
        actualSymbol = context[actualPos:actualPos + 1:1]
        #Now we have actual symbol like ;, A or #
        #Now we need to do ContextLookup
        contextLookup = ContextLookup.objects.get(symbol=actualSymbol)
        symbolValue = contextLookup.cvalue # ie 2222
        if len(symbolValue) != 4:
            raise Exception("Unmatched Length")
        return int(symbolValue[offsetPos:offsetPos + 1:1])
        
    def _system_auth_is_allowable_(trace_obj=None, **kwargs):
        #All Do not Cares
        contextManager = ContextManager.objects.all()[0]
        temp_obj = {'type': 'System'}
        if trace_obj:
            val = AUTH_DECISION['ALLOW'] if contextManager.defaultXValue else AUTH_DECISION['DENY']
            index = len(trace_obj)
            temp_obj['action'] = val
            trace_obj[index] = temp_obj
        return contextManager.defaultXValue

    def _group_auth_is_allowable_helper_(group, pos, trace_obj=None, **kwargs):
        temp_obj = {'type': 'Group', 'id': group.id}
        if group:
            parent = group.parent
            if group.role:
                #decision 1=>ALLOW, 0 => DENY, 2 => DO_NOT_CARE
                #group hierarchy need to be handled prior final decision on DO_NOT_CARES
                decision = Authorization._auth_get_context_decision_(group.role.context, pos)
                if decision == AUTH_DECISION['ALLOW']:
                    if trace_obj:
                        index = len(trace_obj)
                        temp_obj['action'] = AUTH_DECISION['ALLOW']
                        trace_obj[index] = temp_obj
                    return True
                elif decision == AUTH_DECISION['DENY']:
                    if trace_obj:
                        index = len(trace_obj)
                        temp_obj['action'] = AUTH_DECISION['DENY']
                        trace_obj[index] = temp_obj
                    return False
                else:
                    #Must be DoNotCare
                    if trace_obj:
                        index = len(trace_obj)
                        temp_obj['action'] = AUTH_DECISION['DO_NOT_CARE']
                        trace_obj[index] = temp_obj
                    return Authorization._group_auth_is_allowable_helper_(parent, pos, trace_obj, **kwargs)
            else:
                if trace_obj:
                    index = len(trace_obj)
                    temp_obj['action'] = AUTH_DECISION['NO_ROLE']
                    trace_obj[index] = temp_obj
                return Authorization._group_auth_is_allowable_helper_(parent, pos, trace_obj, **kwargs)
        else:
            return Authorization._system_auth_is_allowable_(trace_obj, **kwargs)

    def _group_auth_is_allowable_(user, pos, trace_obj=None, **kwargs):
        group = user.group
        return Authorization._group_auth_is_allowable_helper_(group, pos, trace_obj, **kwargs)

    def _jobtitle_auth_is_allowable_(user, pos, trace_obj=None, **kwargs):
        jobtitle = user.job_title
        temp_obj = {'type': 'JobTitle', 'id': jobtitle.id}
        if not jobtitle:
            #We need to pass to group, user has no job_title
            return Authorization._group_auth_is_allowable_(user, pos, trace_obj, **kwargs)
        if jobtitle.role:
            #decision 1=>ALLOW, 0 => DENY, 2 => DO_NOT_CARE
            decision = Authorization._auth_get_context_decision_(jobtitle.role.context, pos)
            if decision == AUTH_DECISION['ALLOW']:
                if trace_obj:
                    index = len(trace_obj)
                    temp_obj['action'] = AUTH_DECISION['ALLOW']
                    trace_obj[index] = temp_obj
                return True
            elif decision == AUTH_DECISION['DENY']:
                if trace_obj:
                    index = len(trace_obj)
                    temp_obj['action'] = AUTH_DECISION['DENY']
                    trace_obj[index] = temp_obj
                return False
            else:
                # Must be DoNotCare
                if trace_obj:
                    index = len(trace_obj)
                    temp_obj['action'] = AUTH_DECISION['DO_NOT_CARE']
                    trace_obj[index] = temp_obj
                return Authorization._group_auth_is_allowable_(user, pos, trace_obj, **kwargs)
        else:
            #We need to pass to group, user has a jobtitle with no roles
            if trace_obj:
                    index = len(trace_obj)
                    temp_obj['action'] = AUTH_DECISION['NO_ROLE']
                    trace_obj[index] = temp_obj
            return Authorization._group_auth_is_allowable_(user, pos, trace_obj, **kwargs)
        
    def _user_auth_is_allowable_(user, pos, trace_obj=None, **kwargs):
        temp_obj = {'type': 'User', 'id': user.id}
        if user.role:
            #decision 1=>ALLOW, 0 => DENY, 2 => DO_NOT_CARE
            decision = Authorization._auth_get_context_decision_(user.role.context, pos)
            if decision == AUTH_DECISION['ALLOW']:
                if trace_obj:
                    index = len(trace_obj)
                    temp_obj['action'] = AUTH_DECISION['ALLOW']
                    trace_obj[index] = temp_obj
                return True
            elif decision == AUTH_DECISION['DENY']:
                if trace_obj:
                    index = len(trace_obj)
                    temp_obj['action'] = AUTH_DECISION['DENY']
                    trace_obj[index] = temp_obj
                return False
            else:
                #Must be DO_NOT_CARE
                if trace_obj:
                    index = len(trace_obj)
                    temp_obj['action'] = AUTH_DECISION['DO_NOT_CARE']
                    trace_obj[index] = temp_obj
                return Authorization._jobtitle_auth_is_allowable_(user, pos, trace_obj, **kwargs)
        else:
            #We need to move to job_title
            if trace_obj:
                index = len(trace_obj)
                temp_obj['action'] = AUTH_DECISION['NO_ROLE']
                trace_obj[index] = temp_obj
            return Authorization._jobtitle_auth_is_allowable_(user, pos, trace_obj, **kwargs)

    ###ENTRY POINT###
    def _auth_is_allowable_(user, opname, trace_obj=None, **kwargs):
        # trace_obj , initialize with {}
        # For Authenticated users only
        if not user.is_authenticated:
            return False
        #1. If superuser return True
        if user.is_superuser:
            return True
        #2. pos = Get Position of the opname
        contextPosition = ContextPosition.objects.filter(cName=opname)
        if not contextPosition:
            return False #No rule defined
        #3.Checking user roles
        return Authorization._user_auth_is_allowable(user, contextPosition.cPosition, trace_obj, **kwargs)
    

    ##Decorator functions here
    #use this in your html template
    # contains user as an object return true or false
    # non-decorator
    def authorize_client(user, name, **kwargs):
        # user a user object found in client
        # name ie product_search
        return Authorization._auth_is_allowable_(user, name, **kwargs)

    #Contains request and return response
    # use this in views.py file
    # this is a decorator function
    def authorize_server(name, **arg_dict):
        """
        Method accepts
            name : ie add_product
            the following are options
                **arg_dict['opt_redirect'] ie 'authorization:not_allowed'
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                request = args[0]
                decision = Authorization._auth_is_allowable_(request.user, name, **kwargs)
                print("Decision is ", decision)
                if decision:
                    return func(*args, **kwargs)
                else:
                    redirect_url = arg_dict['opt_redirect'] if 'opt_redirect' in arg_dict else 'authorization:not_allowed'
                    return redirect(redirect_url)
            return wrapper
        return decorator