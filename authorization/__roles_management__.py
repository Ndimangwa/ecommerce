from .__authorization_constants__ import AUTH_DECISION, AUTH_REVERSE_DECISION, BLOCK_SIZE
from .models import Roles, ContextLookup, ContextPosition

class RolesManager:
    def __set_permission__(role_obj, rule_name, action, **kwargs):
        """
        This function received
            role : a Roles object
            rule_name : the name of the rule , a string value, ie 'add_user'
            action : an int value, ALLOW, DENY, DO_NOT_CARE as defined in AUTH_DECISION
            **kwargs : an other variables

            return a role which has been updated, if rule_name not found, the role object will be untouched
        """
        #Step 1: Check if role
        if role_obj is None:
            return None
        #Step 2: Cet pos based on the rulename
        contextPosition1 = ContextPosition.objects.get(cName=rule_name)
        if contextPosition1 is None:
            return role_obj
        pos = contextPosition1.cPosition
        #Step 3: Get actualPos and offsetPos
        actualPos = pos // BLOCK_SIZE
        offsetPos = pos % BLOCK_SIZE
        #Step 4: Get contextString
        contextString = role_obj.context
        if actualPos >= len(contextString):
            raise Exception("Unsupported position in the context")
        original_length_of_context_string = len(contextString)
        #Now we are moving to a serious math
        #Step 5: get-actual-symbo , like !
        actualSymbol = contextString[actualPos:actualPos+1:1]
        #Step 6: get-context-series ie ; is 2222
        #Now we have actual symbol like ;, A or #
        #Now we need to do ContextLookup
        tContextLookup = ContextLookup.objects.filter(symbol=actualSymbol)
        #We need to differentiate between 'A' and 'a'
        if tContextLookup is None:
            raise Exception("Lookup Not Found")
        contextLookup1 = tContextLookup[0] if actualSymbol == tContextLookup[0].symbol else tContextLookup[1] if len(tContextLookup) == 2 and actualSymbol == tContextLookup[1].symbol else None
        if contextLookup1 is None:
            raise Exception("Failed to Selected between 'a' and 'A'")
        symbolValue = contextLookup1.cvalue # ie 2222
        if len(symbolValue) != BLOCK_SIZE:
            raise Exception("Unmatched Length")
        try:
            action = int(action)
        except:
            raise Exception("Integer value for action expected")
        if action not in AUTH_REVERSE_DECISION:
            raise Exception("Unsupported Action")
        symbolValue = symbolValue[:offsetPos] + str(action) + symbolValue[offsetPos + 1:]
        #Now we need to go back to Lookup to get this new Symbol
        contextLookup1 = ContextLookup.objects.get(cvalue=symbolValue)
        if contextLookup1 is None:
            raise Exception("Calculated symbolValue could not get its ContextLookup object")
        actualSymbol = contextLookup1.symbol
        #We just need to update the contextString
        contextString = contextString[:actualPos] + actualSymbol + contextString[actualPos+1:]
        #We need to finalize this role_obj
        if len(contextString) != original_length_of_context_string:
            raise Exception("Math Manipulation Error")
        role_obj.context = contextString
        role_obj.save()
        return role_obj
