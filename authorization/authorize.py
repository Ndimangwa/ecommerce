from .models import ContextManager, ContextLookup, ContextPosition

AUTH_DECISION = {
    'ALLOW' : 1,
    'DENY' : 0,
    'DO_NOT_CARE' : 2,
}

class Authorization:
    #Low level authorization
    def _auth_get_context_decision_(self, context, pos):
        BLOCK_SIZE = 4
        actualPos = pos // BLOCK_SIZE
        offsetPos = pos % BLOCK_SIZE
        if actualPos >= len(context):
            raise Exception("Unsupported position in the context")
        actualSymbol = context[actualPos:actualPos + 1:1]
        #Now we have actual symbol like ;, A or #
        #Now we need to do ContextLookup
        contextLookup = ContextLookup.objects.get(symbol=actualSymbol)
        symbolValue = contextLookup.cvalue
        if len(symbolValue) != 4:
            raise Exception("Unmatched Length")
        return int(symbolValue[offsetPos:offsetPos + 1:1])
        
    def _system_auth_is_allowable_(self, **kwargs):
        #All Do not Cares
        contextManager = ContextManager.objects.all()[0]
        return contextManager.defaultXValue

    def _group_auth_is_allowable_helper_(self, group, pos, **kwargs):
        if group:
            parent = group.parent
            if group.role:
                #decision 1=>ALLOW, 0 => DENY, 2 => DO_NOT_CARE
                #group hierarchy need to be handled prior final decision on DO_NOT_CARES
                decision = self._auth_get_context_decision_(group.role.context, pos)
                if decision == AUTH_DECISION['ALLOW']:
                    return True
                elif decision == AUTH_DECISION['DENY']:
                    return False
                else:
                    #Must be DoNotCare
                    return self._group_auth_is_allowable_helper_(parent, **kwargs)
            else:
                return self._group_auth_is_allowable_helper_(parent, **kwargs)
        else:
            return self._system_auth_is_allowable_(**kwargs)

    def _group_auth_is_allowable_(self, user, pos, **kwargs):
        group = user.group
        return self._group_auth_is_allowable_helper_(group, pos, **kwargs)

    def _jobtitle_auth_is_allowable_(self, user, pos, **kwargs):
        jobtitle = user.job_title
        if not jobtitle:
            #We need to pass to group, user has no job_title
            return self._group_auth_is_allowable_(user, pos, **kwargs)
        if jobtitle.role:
            #decision 1=>ALLOW, 0 => DENY, 2 => DO_NOT_CARE
            decision = self._auth_get_context_decision_(jobtitle.role.context, pos)
            if decision == AUTH_DECISION['ALLOW']:
                return True
            elif decision == AUTH_DECISION['DENY']:
                return False
            else:
                # Must be DoNotCare
                return self._group_auth_is_allowable_(user, pos, **kwargs)
        else:
            #We need to pass to group, user has a jobtitle with no roles
            return self._group_auth_is_allowable_(user, pos, **kwargs)
        
    def _user_auth_is_allowable_(self, user, pos, **kwargs):
        if user.role:
            #decision 1=>ALLOW, 0 => DENY, 2 => DO_NOT_CARE
            decision = self._auth_get_context_decision_(user.role.context, pos)
            if decision == AUTH_DECISION['ALLOW']:
                return True
            elif decision == AUTH_DECISION['DENY']:
                return False
            else:
                #Must be DO_NOT_CARE
                return self._jobtitle_auth_is_allowable_(user, pos, **kwargs)
        else:
            #We need to move to job_title
            return self._jobtitle_auth_is_allowable_(user, pos, **kwargs)

    ###ENTRY POINT###
    def _auth_is_allowable_(self, user, opname, **kwargs):
        #1. If superuser return True
        if user.is_superuser:
            return True
        #2. pos = Get Position of the opname
        contextPosition = ContextPosition.objects.get(cName=opname)
        #3.Checking user roles
        return self._user_auth_is_allowable(user, contextPosition.cPosition, **kwargs)