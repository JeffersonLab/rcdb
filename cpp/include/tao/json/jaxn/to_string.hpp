// Copyright (c) 2017 Dr. Colin Hirsch and Daniel Frey
// Please see LICENSE for license or visit https://github.com/taocpp/json/

#ifndef TAOCPP_JSON_INCLUDE_JAXN_TO_STRING_HPP
#define TAOCPP_JSON_INCLUDE_JAXN_TO_STRING_HPP

#include <sstream>

#include "../value.hpp"
#include "to_stream.hpp"

namespace tao
{
   namespace json
   {
      namespace jaxn
      {
         template< template< typename... > class Traits >
         std::string to_string( const basic_value< Traits >& v )
         {
            std::ostringstream o;
            jaxn::to_stream( o, v );
            return o.str();
         }

         template< template< typename... > class Traits >
         std::string to_string( const basic_value< Traits >& v, const unsigned indent )
         {
            std::ostringstream o;
            jaxn::to_stream( o, v, indent );
            return o.str();
         }

      }  // namespace jaxn

   }  // namespace json

}  // namespace tao

#endif
