// Copyright (c) 2017 Dr. Colin Hirsch and Daniel Frey
// Please see LICENSE for license or visit https://github.com/taocpp/json/

#ifndef TAOCPP_JSON_INCLUDE_EVENTS_JSON_CBOR_TO_STRING_HPP
#define TAOCPP_JSON_INCLUDE_EVENTS_JSON_CBOR_TO_STRING_HPP

#include <sstream>

#include "to_stream.hpp"

namespace tao
{
   namespace json
   {
      namespace events
      {
         namespace cbor
         {
            struct to_string
               : public to_stream
            {
               std::ostringstream oss;

               to_string()
                  : to_stream( oss )
               {
               }

               std::string value() const
               {
                  return oss.str();
               }
            };

         }  // namespace cbor

      }  // namespace events

   }  // namespace json

}  // namespace tao

#endif
