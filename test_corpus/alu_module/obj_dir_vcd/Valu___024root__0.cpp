// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Valu.h for the primary calling header

#include "Valu__pch.h"

bool Valu___024root___trigger_anySet__act(const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Valu___024root___trigger_anySet__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        if (in[n]) {
            return (1U);
        }
        n = ((IData)(1U) + n);
    } while ((1U > n));
    return (0U);
}

void Valu___024root___trigger_orInto__act_vec_vec(VlUnpacked<QData/*63:0*/, 1> &out, const VlUnpacked<QData/*63:0*/, 1> &in) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Valu___024root___trigger_orInto__act_vec_vec\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = (out[n] | in[n]);
        n = ((IData)(1U) + n);
    } while ((0U >= n));
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Valu___024root___dump_triggers__act(const VlUnpacked<QData/*63:0*/, 1> &triggers, const std::string &tag);
#endif  // VL_DEBUG

bool Valu___024root___eval_phase__act(Valu___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Valu___024root___eval_phase__act\n"); );
    Valu__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    {
        // Inlined CFunc: _eval_triggers_vec__act
        vlSelfRef.__VactTriggered[0U] = (QData)((IData)(
                                                        ((((~ (IData)(vlSelfRef.rst_n)) 
                                                           & (IData)(vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0)) 
                                                          << 1U) 
                                                         | ((IData)(vlSelfRef.clk) 
                                                            & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__clk__0))))));
        vlSelfRef.__Vtrigprevexpr___TOP__clk__0 = vlSelfRef.clk;
        vlSelfRef.__Vtrigprevexpr___TOP__rst_n__0 = vlSelfRef.rst_n;
    }
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Valu___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
    }
#endif
    Valu___024root___trigger_orInto__act_vec_vec(vlSelfRef.__VnbaTriggered, vlSelfRef.__VactTriggered);
    return (0U);
}

void Valu___024root___trigger_clear__act(VlUnpacked<QData/*63:0*/, 1> &out) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Valu___024root___trigger_clear__act\n"); );
    // Locals
    IData/*31:0*/ n;
    // Body
    n = 0U;
    do {
        out[n] = 0ULL;
        n = ((IData)(1U) + n);
    } while ((1U > n));
}

bool Valu___024root___eval_phase__nba(Valu___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Valu___024root___eval_phase__nba\n"); );
    Valu__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = Valu___024root___trigger_anySet__act(vlSelfRef.__VnbaTriggered);
    if (__VnbaExecute) {
        {
            // Inlined CFunc: _eval_nba
            if ((3ULL & vlSelfRef.__VnbaTriggered[0U])) {
                {
                    // Inlined CFunc: _nba_sequent__TOP__0
                    if (vlSelfRef.rst_n) {
                        vlSelfRef.zero = (0U == vlSelfRef.result);
                        if (VL_UNLIKELY(((8U & (IData)(vlSelfRef.op))))) {
                            VL_WRITEF_NX("[%0t] %%Error: alu.sv:46: Assertion failed in %m: ALU: Illegal opcode 4'b%b executed at time %0t\n",5, 'M',vlSymsp->name(),"alu", 'T',-12
                                         , '#',64,VL_TIME_UNITED_Q(1)
                                         , '#',4,(IData)(vlSelfRef.op)
                                         , '#',64,VL_TIME_UNITED_Q(1));
                            VL_STOP_MT("alu.sv", 46, "");
                            vlSelfRef.result = 0U;
                        } else if ((4U & (IData)(vlSelfRef.op))) {
                            if ((2U & (IData)(vlSelfRef.op))) {
                                if (VL_UNLIKELY(((1U 
                                                  & (IData)(vlSelfRef.op))))) {
                                    VL_WRITEF_NX("[%0t] %%Error: alu.sv:46: Assertion failed in %m: ALU: Illegal opcode 4'b%b executed at time %0t\n",5, 'M',vlSymsp->name(),"alu", 'T',-12
                                                 , '#',64,VL_TIME_UNITED_Q(1)
                                                 , '#',4,(IData)(vlSelfRef.op)
                                                 , '#',64,VL_TIME_UNITED_Q(1));
                                    VL_STOP_MT("alu.sv", 46, "");
                                    vlSelfRef.result = 0U;
                                } else {
                                    vlSelfRef.result 
                                        = (vlSelfRef.a 
                                           >> (0x0000001fU 
                                               & vlSelfRef.b));
                                }
                            } else {
                                vlSelfRef.result = 
                                    ((1U & (IData)(vlSelfRef.op))
                                      ? (vlSelfRef.a 
                                         << (0x0000001fU 
                                             & vlSelfRef.b))
                                      : (vlSelfRef.a 
                                         ^ vlSelfRef.b));
                            }
                        } else if ((2U & (IData)(vlSelfRef.op))) {
                            vlSelfRef.result = ((1U 
                                                 & (IData)(vlSelfRef.op))
                                                 ? 
                                                (vlSelfRef.a 
                                                 | vlSelfRef.b)
                                                 : 
                                                (vlSelfRef.a 
                                                 & vlSelfRef.b));
                        } else if ((1U & (IData)(vlSelfRef.op))) {
                            vlSelfRef.result = (vlSelfRef.a 
                                                - vlSelfRef.b);
                            vlSelfRef.overflow = (vlSelfRef.a 
                                                  < vlSelfRef.b);
                        } else {
                            vlSelfRef.overflow = (1U 
                                                  & (IData)(
                                                            (1ULL 
                                                             & (((QData)((IData)(vlSelfRef.a)) 
                                                                 + (QData)((IData)(vlSelfRef.b))) 
                                                                >> 0x00000020U))));
                            vlSelfRef.result = (vlSelfRef.a 
                                                + vlSelfRef.b);
                        }
                    } else {
                        vlSelfRef.result = 0U;
                        vlSelfRef.zero = 1U;
                        vlSelfRef.overflow = 0U;
                    }
                }
            }
        }
        Valu___024root___trigger_clear__act(vlSelfRef.__VnbaTriggered);
    }
    return (__VnbaExecute);
}

void Valu___024root___eval(Valu___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Valu___024root___eval\n"); );
    Valu__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Locals
    IData/*31:0*/ __VnbaIterCount;
    // Body
    __VnbaIterCount = 0U;
    do {
        if (VL_UNLIKELY(((0x00002710U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Valu___024root___dump_triggers__act(vlSelfRef.__VnbaTriggered, "nba"s);
#endif
            VL_FATAL_MT("alu.sv", 2, "", "DIDNOTCONVERGE: NBA region did not converge after '--converge-limit' of 10000 tries");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        vlSelfRef.__VactIterCount = 0U;
        do {
            if (VL_UNLIKELY(((0x00002710U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Valu___024root___dump_triggers__act(vlSelfRef.__VactTriggered, "act"s);
#endif
                VL_FATAL_MT("alu.sv", 2, "", "DIDNOTCONVERGE: Active region did not converge after '--converge-limit' of 10000 tries");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U) 
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactPhaseResult = Valu___024root___eval_phase__act(vlSelf);
        } while (vlSelfRef.__VactPhaseResult);
        vlSelfRef.__VnbaPhaseResult = Valu___024root___eval_phase__nba(vlSelf);
    } while (vlSelfRef.__VnbaPhaseResult);
}

#ifdef VL_DEBUG
void Valu___024root___eval_debug_assertions(Valu___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Valu___024root___eval_debug_assertions\n"); );
    Valu__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (VL_UNLIKELY(((vlSelfRef.clk & 0xfeU)))) {
        Verilated::overWidthError("clk");
    }
    if (VL_UNLIKELY(((vlSelfRef.rst_n & 0xfeU)))) {
        Verilated::overWidthError("rst_n");
    }
    if (VL_UNLIKELY(((vlSelfRef.op & 0xf0U)))) {
        Verilated::overWidthError("op");
    }
}
#endif  // VL_DEBUG
