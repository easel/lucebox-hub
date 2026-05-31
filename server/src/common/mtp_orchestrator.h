// Generic MTP warm + decode driver.

#pragma once

#include "model_backend.h"
#include "mtp_interface.h"

namespace dflash::common::mtp {

GenerateResult warm_and_decode(ModelBackend * backend,
                                const GenerateRequest & req,
                                const DaemonIO & io);

}  // namespace dflash::common::mtp
