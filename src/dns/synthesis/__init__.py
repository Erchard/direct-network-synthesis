"""Direct synthesis prototypes and linear algebra utilities."""

__all__ = [
    "DNS04Config",
    "DNS04Synthesizer",
    "DNS05KernelCompiler",
    "KernelSpec",
]


def __getattr__(name: str):
    if name in {"DNS04Config", "DNS04Synthesizer"}:
        from dns.synthesis.dns04 import DNS04Config, DNS04Synthesizer

        return {"DNS04Config": DNS04Config, "DNS04Synthesizer": DNS04Synthesizer}[name]
    if name in {"DNS05KernelCompiler", "KernelSpec"}:
        from dns.synthesis.dns05_kernel_compiler import DNS05KernelCompiler, KernelSpec

        return {"DNS05KernelCompiler": DNS05KernelCompiler, "KernelSpec": KernelSpec}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
