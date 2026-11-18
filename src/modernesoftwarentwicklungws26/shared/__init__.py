"""Shared Kernel: Typen, die mehrere Bounded Contexts gemeinsam verwenden.

Bewusst klein gehalten: nur IDs, die eine Context-Grenze überqueren, und die
Domain-Events, die zwischen Contexts ausgetauscht werden (Übung 3, Kap. 3: ``shared/events``).
So kennen ``identity`` und ``abstimmung`` dieselben Event-Klassen, ohne einander zu importieren.
"""
